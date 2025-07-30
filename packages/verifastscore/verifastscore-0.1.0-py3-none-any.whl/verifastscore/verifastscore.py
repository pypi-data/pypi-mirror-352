import os
import json
import argparse
from collections import defaultdict
import logging
import time

import spacy
from tqdm import tqdm
import torch
import regex as re
import pickle as pkl

from transformers import AutoModelForCausalLM, AutoTokenizer

from verifastscore.search_API import SearchAPI

from verifastscore.prompts.PromptCausalLM import PromptCausalLM

abstain_responses = ["I'm sorry, I cannot fulfill that request.",
                     "I'm sorry, I can't fulfill that request.",
                     "I'm sorry, but I cannot fulfill that request.",
                     "I'm sorry, but I can't fulfill that request.",
                     "Sorry, but I can't fulfill that request.",
                     "Sorry, I can't do that."]

SYSTEM_MESSAGE = '''You are trying to verify how factual a response is by extracting fine-grained, verifiable claims. Each claim must describe one single event or one single state (for example, “Nvidia was founded in 1993 in Sunnyvale, California, U.S.”) in one sentence with at most one embedded clause. Each fact should be understandable on its own and require no additional context. This means that all entities must be referred to by name but not by pronoun. Use the name of entities rather than definite noun phrases (e.g., “the teacher”) whenever possible. If a definite noun phrase is used, be sure to add modifiers (e.g., an embedded clause or a prepositional phrase). Each fact must be situated within relevant temporal and location details whenever needed.

All necessary specific details—including entities, dates, and locations—must be explicitly named, and verify here means that every detail of a claim is directly confirmed by the provided evidence. The verification process involves cross-checking each detail against the evidence; a detail is considered verified if it is clearly confirmed by the evidence.

Avoid extracting stories, personal experiences, hypotheticals (e.g., those using “would be” or the subjunctive mood), subjective opinions, suggestions, advice, instructions, or similarly non-factual content; however, biographical, historical, scientific, and similar texts are acceptable. Also, ignore any listed references.

For each extracted claim, classify it as follows:

Supported: Every detail of the claim (including entities, dates, and locations) is directly confirmed by the provided evidence with no contradictions.
Unsupported: One or more details of the claim are either missing from or contradicted by the provided evidence, even though the claim remains verifiable using external sources.

You do not need to justify what you extract.

Output format:
<fact 1>: <your judgment of fact 1>
<fact 2>: <your judgment of fact 2>
…
<fact n>: <your judgment of fact n>

If no verifiable claim can be extracted, simply output "No verifiable claim."'''
#----------------------------------------------------------
def get_sentence(spacy_nlp, text):
    # use spaCy to split the text into sentences
    return [x.text.strip() for x in spacy_nlp(text).sents]
#----------------------------------------------------------
def extract_response_ids(outputs, input_ids, num_return_sequences=1):
    assert len(outputs)==(len(input_ids)*num_return_sequences)
    response_ids = []
    for inp_idx in range(len(input_ids)):
        for seq_idx in range(num_return_sequences):
            response_ids.append(outputs[seq_idx+inp_idx*num_return_sequences, len(input_ids[inp_idx]):])
    return response_ids
#---------------------------------------------------------- 
class VeriFastScore(object):
    def __init__(self,
        model_name,
        data_dir='./data',
        cache_dir='./data/cache',
        output_dir='./data_cache',
        search_res_num=5
    ): 
        self.median_claims = 17 #Estimated from test set; modify as per need: higher for more factual domains and lesser for less factual domains
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_new_tokens=2048
        self.num_beams=1
        self.do_sample=True
        self.temperature=0.7
        self.top_p=1
        self.num_return_sequences=1
        self.max_length=108000
        self.system_message = SYSTEM_MESSAGE
        self.label_n = 2

        self.model_name = model_name
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
        )
        self.model.eval()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
        )

        self.model = self.model.to(self.device)
    
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.cache_dir = cache_dir

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.spacy_nlp = spacy.load('en_core_web_sm')

        self.fetch_search = SearchAPI()
        self.search_res_num = search_res_num
    
        self.prompter = PromptCausalLM(
            self.model_name,
            self.tokenizer,
            self.max_length,
            self.system_message
        )

    def get_prompt(self, role:str, **args)->str:
        prompt = ""
        if role=="user":
            prompt += "### Response\n" + args["response"]
            prompt += "\n" + "### Evidence\n"
            prompt += args["evidence"]

        elif role=="assistant":
            prompt += "### Facts\n"
            if args["claim_verification_result"]==None or len(args["claim_verification_result"])==0:
                prompt += "No verifiable claim."
                return prompt
            prompt_claims = []
            for claim in args["claim_verification_result"]:
                label_text = "Supported" if claim["verification_result"].lower() == "supported" else "Unsupported"
                prompt_claims.append("{}: {}".format(claim["claim"], label_text))
            prompt += "\n".join(prompt_claims)
        else: 
            raise ValueError("Uncrecognized role: {}".format(role))
        return prompt

    def _extract_judgment(self, response):
        judgmentPattern = r"(?P<claim_text>.+): (?P<judgment>Supported|Unsupported)\n?"
        return re.findall(judgmentPattern, response)

    def get_verifastscore(self, data, input_file_name):
        time_taken = {
            "evidence_retrieval": [],
            "decompose_and_verify": [],
            "verifastscore": []
        }
        #Evidence Retrieval
        output_file = f"evidence_{input_file_name}.jsonl"
        output_path = os.path.join(self.output_dir, output_file)
        searched_evidence_dict = []
        with open(output_path, "w") as f:
            for dict_item in tqdm(data):
                start = time.perf_counter()
                response = dict_item["response"].strip()
                question = dict_item["question"].strip()
                prompt_source = dict_item["prompt_source"]
                model = dict_item["model"]

                # skip abstained responses
                if response.strip() in abstain_responses:
                    output_dict = {"question": question.strip(),
                                   "response": response.strip(),
                                   "abstained": True,
                                   "prompt_source": prompt_source,
                                   "model": model, }
                    end = time.perf_counter()
                    time_taken["evidence_retrieval"].append((end-start))
                    f.write(json.dumps(output_dict) + "\n")
                    continue
                
                if "claim_search_results" not in dict_item:
                    claim_lst = get_sentence(self.spacy_nlp, response)
                    claim_snippets = self.fetch_search.get_snippets(claim_lst)
                    dict_item["claim_search_results"] = claim_snippets
                else:
                    claim_snippets = dict_item["claim_search_results"]
                if "evidence" not in dict_item:
                    dict_item ["evidence"] = ("\n\n".join(["\n".join([search_res["snippet"] if "snippet" in search_res else search_res["title"] for search_res in claim_snippets[sent]]) for sent in claim_snippets]))
                searched_evidence_dict.append(dict_item)
                end = time.perf_counter()
                time_taken["evidence_retrieval"].append((end-start))
                f.write(json.dumps(dict_item) + "\n")
                f.flush()
        print(f"evidence searching is done! saved to {output_path}")

        #Decomposition+Verification
        output_dir = os.path.join(self.output_dir, 'model_output')
        os.makedirs(output_dir, exist_ok=True)
        output_file = f'decomposition_verification_{input_file_name}_{self.label_n}.jsonl'
        output_path = os.path.join(output_dir, output_file)

        verifastscore = []
        with open(output_path, "w") as f:
            for dict_item in tqdm(searched_evidence_dict):
                start = time.perf_counter()
                model_name = dict_item['model']
                domain = dict_item['prompt_source']
                claim_search_results = dict_item["claim_search_results"]

                if "abstained" in dict_item and dict_item['abstained']:
                    end = time.perf_counter()
                    time_taken["decompose_and_verify"].append((end-start))
                    f.write(json.dumps(dict_item) + "\n")
                    continue

                messages = [{
                    "role": "user",
                    "content": self.get_prompt(
                        role="user",
                        response=dict_item["response"].strip(),
                        evidence=dict_item["evidence"]
                    )
                }]

                input_ids, _ = self.prompter.get_inputs(messages)
                outputs = self.model.generate(
                    input_ids=input_ids.to(self.device),
                    attention_mask=torch.ones_like(input_ids).to(self.device),
                    max_new_tokens=self.max_new_tokens,
                    num_beams=self.num_beams,
                    do_sample=self.do_sample,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    num_return_sequences=self.num_return_sequences
                )
                response_ids = extract_response_ids(
                    outputs, 
                    input_ids=input_ids,
                    num_return_sequences=self.num_return_sequences
                )
                responses = self.tokenizer.batch_decode(response_ids, skip_special_tokens=False)
                end = time.perf_counter()
                time_taken["decompose_and_verify"].append((end-start))
                start = time.perf_counter()
                logging.info("Input:\n{}\n\nOutput:\n{}\n****".format(messages[0]["content"], responses[0]))
                prediction = self._extract_judgment(responses[0])
                if len(prediction)==0 or "No verifiable claim".lower() in prediction[0][0].lower():
                    verifastscore.append(0)
                    dict_item["claim_verification_result"] = []
                    end = time.perf_counter()
                    time_taken["verifastscore"].append((end-start))
                    f.write(json.dumps(dict_item) + "\n")
                    continue
                fp = [1 if pred_label[1].lower()=="supported" else 0 for pred_label in prediction]
                precision = sum(fp)/len(fp) if len(fp) else 0
                recall = min(1, (len(fp)/self.median_claims))
                verifastscore.append((2*precision*recall)/(precision+recall))
                claim_verify_res_dict = []
                for pred in prediction:
                    claim_verify_res_dict.append({
                        "claim": pred[0],
                        "verification_result": pred[1].lower()
                    })
                dict_item["claim_verification_result"] = claim_verify_res_dict
                end = time.perf_counter()
                time_taken["verifastscore"].append((end-start))
                f.write(json.dumps(dict_item) + "\n")
        if len(verifastscore):
            print("VeriFastScore: {:0.4f} ({} instances)".format(sum(verifastscore)/len(verifastscore), len(verifastscore)))
        return time_taken
#----------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default='./data')
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default='./data')
    parser.add_argument("--cache_dir", help="Deprecated. Cache at data/cache/", type=str, default='./data/cache')
    parser.add_argument("--model_name", type=str, default="rishanthrajendhran/VeriFastScore")
    parser.add_argument("--search_res_num", type=int, default=10)
    args = parser.parse_args()

    logging.basicConfig(filemode='w', level=logging.INFO)

    vfs = VeriFastScore(
        model_name=args.model_name,
        data_dir=args.data_dir,
        cache_dir=args.cache_dir,
        output_dir=args.output_dir,
        search_res_num=args.search_res_num,
    )

    input_file_name = "".join(args.input_file.split('.')[:-1])
    input_path = os.path.join(args.data_dir, args.input_file)
    with open(input_path, "r") as f:
        data = [json.loads(x) for x in f.readlines() if x.strip()]

    start = time.perf_counter()
    time_taken = vfs.get_verifastscore(data, input_file_name)
    end = time.perf_counter()
    print("Total time taken: {:.6f}s".format(end-start))
    print("Avg time/instance: {:.6f}s".format((end-start)/len(data)))
    print("Total time per stage")
    print("\tEvidence Retrieval: {:0.6f}".format(sum(time_taken["evidence_retrieval"])))
    print("\tDecompose and Verify: {:0.6f}".format(sum(time_taken["decompose_and_verify"])))
    print("Avg time per stage per instance")
    print("\tEvidence Retrieval: {:0.6f}".format(sum(time_taken["evidence_retrieval"])/len(time_taken["evidence_retrieval"])))
    print("\tDecompose and Verify: {:0.6f}".format(sum(time_taken["decompose_and_verify"])/len(time_taken["decompose_and_verify"])))
    time_dir = os.path.join(args.output_dir, 'time')
    os.makedirs(time_dir, exist_ok=True)
    time_file = f'verifastscore_time_{input_file_name}_2.pkl'
    time_path = os.path.join(time_dir, time_file)
    with open(time_path, "wb") as f:
        pkl.dump(time_taken, f)
#----------------------------------------------------------
if __name__ == '__main__':
    main()