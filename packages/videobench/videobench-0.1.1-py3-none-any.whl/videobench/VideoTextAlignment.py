import os
from typing import List, Dict, Any
from tqdm import tqdm
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import re
import json
import yaml
import logging
import tenacity
from tenacity import retry, stop_after_attempt, wait_random_exponential
from openai import OpenAI
from .utils import Video_Dataset

class Agent():
    def __init__(self, agent, logger, prompt, config) -> None:
        """
        initialize agents, including functions that initiate chats and mllm calling
        agents: list of strings, each string is the name of an agent
        logger: logger object
        prompt: dict, system prompt, user prompt, and summary prompt
        config: dict, configurations
        """
        self.agent = agent
        self.logger = logger
        self.prompt = prompt
        self.config = config
        self.video_prompt=''
        self.history = []
        self.completion_tokens = 0
        self.prompt_tokens = 0

        # openai configurations
        self.api_key = self.config['GPT4o_mini_API_KEY']
        self.base_url = self.config['GPT4o_mini_BASE_URL']
        self.model = "gpt-4o-mini"

    # reset everything, avoid initializing too many classes
    def reset(self):
        self.video_prompt = ''
        self.history = []
        self.completion_tokens = 0
        self.prompt_tokens = 0

    @tenacity.retry(wait=tenacity.wait_exponential(max=60),
                    stop=tenacity.stop_after_attempt(5),
                    retry=tenacity.retry_if_exception_type(TypeError),
                    reraise=True)

        # call openai, input messages, get response
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def call_oai(self, mess):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=mess,
            temperature=0
        )
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens

        self.completion_tokens += completion_tokens
        self.prompt_tokens += prompt_tokens

        return response.choices[0].message.content

    def prepare_message_text(self,agent):
        
        self.video_prompt = f'This is the text prompt:\n{self.video_prompt}'
        if not self.history:
            message_ = 'It\'s the first round.' + self.prompt[agent]+self.video_prompt
        # if not, get the history, and concat everything with proper format
        else:
            #prefix = ''
            # Create a header for the history section
            history_header = "There are the detailed video descriptions of the video:\n\n"
            history_content = '\n'.join(self.history)
            # Combine the header with the content
            history_ = history_header + "<video's description>\n" + history_content + "\n</video's description>"
            # Construct the final message with the provided prefix, history, and prompts
            message_ = self.video_prompt + '\n\n' + history_
        self.messages_text=[{"role": "system", "content": self.prompt[agent]},
            {"role": "user", "content": message_+'\n\nYour questions must be deisplayed in the format: \n<question>\n[your questions] or [I have no question]\n</question>.' + '\n\nDisplay the results in the specified Output Format'}]
        return self.messages_text


    def chat_for_one_round_text(self, agent) -> str:
        self.logger.info(f'-----Agent:{agent}-----')
        message = self.prepare_message_text(agent)
        response = self.call_oai(message)
        #self.history.append(response)
        self.logger.info(f'Round of {agent}:{response}')
        return response

# summarize the conversation and get the results

class Host():
    def __init__(self, name: str, logger, prompt, config, modelname,modelmessage,agents: List[Agent]):
        self.name = name
        self.agents = agents
        self.logger = logger
        self.prompt = prompt
        self.config = config
        self.modelname = modelname
        self.modelmessage = modelmessage
        self.video_prompt=" "
        self.frames=[]
        self.history = []
        self.qa_history = []
        self.description = ''
        self.api_key = self.config['GPT4o_API_KEY']
        self.base_url = self.config['GPT4o_BASE_URL']
        self.model = "gpt-4o-2024-08-06"
        self.completion_tokens = 0
        self.prompt_tokens = 0

    def reset(self):
        self.history = []
        self.qa_history = []
        self.frames=[]
        self.video_prompt = " "
        self.description = ''
        self.messages = []
        self.completion_tokens = 0
        self.prompt_tokens = 0

    def call_oai(self, mess):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # client = AzureOpenAI(api_key=self.api_key, api_version=self.api_version, azure_endpoint=self.azure_endpoint)
        response = client.chat.completions.create(
            model=self.model,
            messages=mess,
            temperature=0
        )
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens

        self.completion_tokens += completion_tokens
        self.prompt_tokens += prompt_tokens

        return response.choices[0].message.content

    def initial_result(self):
        self.video_prompt = f'This is the text prompt:\n{self.video_prompt}'
        message_ = "You must think following the 'Evaluation Steps' one by one.\n"
        self.messages = [{"role": "system", "content": self.prompt['gpt4o-system']},
                         {"role": "user", "content": [
                             {"type": "text", "text": message_},
                             {"type": "text", "text": '\n\nThese are the frames from the video generated by {}\n'.format(self.modelname)},
                             {"type": "text", "text": self.modelmessage},
                             *map(lambda x: {"type": "image_url",
                                             "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                                  self.frames[self.modelname])
                         ]}]
 
        self.logger.info('==============initial response============')
        response = self.call_oai(self.messages)
        match = re.search(r'\[Video Description\]:\s*(.*)', response, re.DOTALL)
        if match:
            video_description = match.group(1).strip()
            self.history.append(f"This is the initial information: \n{video_description}\n\n")
        else:
            self.logger.warning("No video captured Description")
            video_description = "No video captured Description"
            self.history.append(f"This is the initial information: \n{video_description}\n\n")
        self.description = f'This is the video\'s initial description:\n<description>\n{response}\n</description>'
        return response

    def get_question(self, response):
        pattern = r"\[Your questions?\]:\s*(.*)"

        # 搜索并提取 [Your question]: 或 [Your questions]: 后的内容
        result = re.search(pattern, response, re.DOTALL)

        if result:
            # 提取 [Your question]: 或 [Your questions]: 后面的所有内容
            question = result.group(1).strip()
            return question
        else:
            # 如果没有匹配到 [Your question]: 或 [Your questions]:，返回 None
            return None

    def question(self) :

        # 1. 各智能体独立获得响应并添加到各自的历史记录中
        self.logger.info('==============agent qa_history============')
        # 2. 按顺序让每个智能体基于当前的历史记录做出回答
        #self.logger.info('==============reflect============')
        for i, agent in enumerate(self.agents):
            #combined_history = "\n".join(self.description)
            #print(combined_history)
            agent.history.append(self.description)
            response = agent.chat_for_one_round_text(agent.agent)
            question = self.get_question(response)
            self.qa_history.append(f"This is the question of the {agent.agent}: {question}\n")
            self.description = self.description+f'\nThis is a question of another assistant:\n<question-one>\n{question}\n</question-one>'

        return self.qa_history

    def answer(self):
        qa_history_header = '\n\nThere are the questions of two assistants:\n\n'
        qa_history_content = '\n'.join(self.qa_history)
        qa_history = qa_history_header + "<qa_history>\n" + qa_history_content + "\n</qa_history>\n"
        self.messages = [{"role": "system", "content":self.prompt['gpt4o-answer']},
                         {"role": "user", "content": [
                             {"type": "text", "text": self.video_prompt},
                             {"type": "text", "text": qa_history},
                             {"type": "text", "text": 'These are the frames from the video generated by {}\n'.format(self.modelname)},
                             # {"type": "text", "text": f"{self.modelmessage}; Please carefully observe whether the actions required by the text prompt appear in the video\n"},
                             {"type": "text", "text": f"{self.modelmessage}\n"},
                             *map(lambda x: {"type": "image_url",
                                             "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                                  self.frames[self.modelname])
                         ]}]
        # print(messages)
        self.logger.info('==============qa_history============')
        response = self.call_oai(self.messages)
        match = re.search(r'\[Descriptions\]:(.*?)\[Answers\]', response, re.DOTALL)
        if match:
            description = match.group(1).strip()  # 提取匹配的内容并去除首尾空格
        else:
            print("No information found.")
        self.qa_history.append(f"\nThis is the answer of the questions: {response}\n\n")
        self.history.append(f"\nThis is the second information: {description}")
        #self.logger.info(f'>>>>>>>>>>qa_history:\n' + self.qa_history)
        return response
    
    def summarize_and_get_results(self) -> str:
        self.logger.info('==============final evaluation results============')
        #self.video_prompt = f'This is the text prompt:\n{self.video_prompt}\n'
        history_header = "There are the two informations:\n"
        history_content = '\n'.join(self.history)
        # Combine the header with the content
        history_ = history_header + "<history>\n" + history_content + "\n</history>"
        #history_ = 'This is the their evaluation history:\n\n<history>\n'.join(self.history)
        message_ = "You must think following the 'evaluation steps' one by one.\n\n" + history_ + '\n\n' + self.video_prompt+'\n\n'
        self.messages = [{"role": "system", "content": self.prompt['summer-system']},
                         {"role": "user", "content":[
                             {"type": "text", "text": message_},
                             {"type": "text", "text": f"{self.modelmessage}\n"},
                             *map(lambda x: {"type": "image_url",
                                             "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                                  self.frames[self.modelname]),
                             {"type": "text", "text": 'The name of the AI medel is {}\n'.format(self.modelname)}
                         ]
                            }]
        #print(messages)
        response = self.call_oai(self.messages)
        return response

# 处理输出结果，按指定格式提取所需内容
def extract_content_from_result(final_result):
    content_des = ""
    content_score = "None"  # 初始化为 "error"
    start_index = final_result.find("Updated Video Description")
    
    if start_index != -1:
        # 提取 "Updated Video Description" 后面的内容
        all_content = final_result[start_index + len("Updated Video Description"):].strip()

        # 找到第一个字母的位置
        first_letter_index = next((i for i, char in enumerate(all_content) if char.isalpha()), None)
        if first_letter_index is not None:
            all_content = all_content[first_letter_index:].strip()

        while True:
            eval_result_index = all_content.find("Evaluation Result")
            if eval_result_index != -1:
                # 提取描述部分
                # content_des = all_content[:eval_result_index].strip()
                remaining_content = all_content[eval_result_index + len("Evaluation Result"):].strip()

                # 查找 "because"
                because_index = remaining_content.find("because")
                if because_index != -1:
                    # 提取 "because" 前的内容
                    before_because = remaining_content[:because_index].strip()

                    # 找到离 "because" 最近的数字
                    for i in range(len(before_because) - 1, -1, -1):
                        if before_because[i].isdigit():
                            content_score = int(before_because[i])
                            break

                    # 如果找到评分，则退出循环
                    if content_score != "error":
                        break
                else:
                    print("未找到 'because'")
                    break
            else:
                print("未找到更多 'Evaluation Result' 部分")
                break
    else:
        print("未找到 'Updated Video Description' 部分")

    return content_score

def eval(config, prompt, dimension, cur_full_info_path,models):
    """
    Evaluate video-text consistency
    
    Args:
        config: Configuration dictionary
        prompt: Evaluation prompt
        dimension: Evaluation dimension
        cur_full_info_path: Path to JSON file containing video paths and prompts
                          (Videos will be loaded and processed by Video_Dataset class)
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(config[f'log_path_{dimension}'])
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # load data
    dataset = Video_Dataset(cur_full_info_path)
    
    index = 0
    score = {}
    history = {}
    model_scores = {}

    l1 = list(range(0, len(dataset)))
    for i in l1:
        data = dataset[i]
        modelmessage = f"{len(data['frames'][modelname])} frames from {modelname}."
            
        agents = [Agent('Assistant-one', logger, prompt, config), 
                    Agent('Assistant-two', logger, prompt, config)]
        host = Host('Host', logger, prompt, config, modelname, modelmessage, agents)
        
        for agent in agents:
            agent.video_prompt = data['prompt']
        host.video_prompt = data['prompt']
        host.frames = data['frames']
        
        score[i] = {}
        history[i] = {}
        score[i]['prompt_en'] = data['prompt']

        # 动态获取模型列表
        available_models = list(data['frames'].keys())
        models_to_process = models if models else available_models
        
        for modelname in models_to_process:

            if modelname not in model_scores:
                model_scores[modelname] = {'total_score': 0, 'count': 0}

            # 为自定义模型创建消息

            logger.info(f'>>>>>>>>This is the {i}_{modelname} round>>>>>>>')
            try:
                # 收集初始描述
                init_response = host.initial_result()
                logger.info(f'>>>>>>>>>>initial response:\n{init_response}')
                # 收集问答记录
                questions = host.question()
                logger.info(f'>>>>>>>>>>questions:\n{questions}')
                answers = host.answer()
                logger.info(f'>>>>>>>>>>answers:\n{answers}')
                # 基于描述和问答给出最终评分
                final_result = host.summarize_and_get_results()
                history[i][modelname] = {
                    'initial_response': init_response,
                    'qa_history': questions,
                    'final_result': final_result
                }
                logger.info(f'>>>>>>>the {i}_{modelname} round >>>>>>Discussion and judge:\n' + final_result +'\n')

                # 处理格式以写入json 
                content_score = extract_content_from_result(final_result)
                score[i][modelname] = content_score

                # 将最终评分累加到模型总分中
                model_scores[modelname]['total_score'] += content_score
                model_scores[modelname]['count'] += 1

            except Exception as e:
                logger.info('>>>>>>>>>>>Error occurred during conversation...')
                logger.info('Errormessage: ' + str(e))
                print(f"An error occurred: {e}")
                score[i] = 'Error'

            for agent in agents:
                agent.reset()
            host.reset()

    average_scores = {model: model_scores[model]['total_score'] / model_scores[model]['count']
                  for model in model_scores if model_scores[model]['count'] > 0}

    return {
        'history': history,  # 评估历史记录
        'score': score ,        # 最终评分结果
        'average_scores': average_scores  # 每个模型的平均分
    }

