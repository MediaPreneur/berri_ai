from gpt_index import GPTSimpleVectorIndex 
from langchain import OpenAI, LLMChain
from langchain.schema import AgentAction, AgentFinish
import re
import os
from langchain.agents import initialize_agent, Tool, ZeroShotAgent, AgentExecutor
from typing import Any, List, Optional, Tuple, Union
from berri_ai.QAAgent import QAAgent

class ComplexInformationQA():
  """Base class for Complex Information QA Agent Class"""  

  def __init__(self, index, prompt = None):
    self.index = index 
    tools = [
      Tool(
          name = "QueryingDB",
          func=self.querying_db,
          description="This function takes a query string as input and returns the most relevant answer from the documentation as output"
      )]

    PREFIX = """Answer the following questions as best you can. You have access to the following tools:"""

    SUFFIX = """Begin!

    Question: {input}
    Thought:{agent_scratchpad}"""

    self.prompt = ZeroShotAgent.create_prompt(
          tools, 
          prefix=PREFIX, 
          suffix=SUFFIX, 
          input_variables=["input", "agent_scratchpad"])
    self.tools = tools
    self.llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=self.prompt)
  
  def querying_db(self, query: str):
    response = self.index.query(query)
    response = (response.response, response.source_nodes[0].source_text)
    return response
  
  def run(self, query_string: str):
    llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=self.prompt)
    agent2 = QAAgent(llm_chain=self.llm_chain, tools=self.tools)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent2, tools=self.tools, verbose=True, return_intermediate_steps=True)
    answer = agent_executor({"input":query_string})
    return answer