# 🍇 Berri AI: 1-click deploy for your LLM Apps ⚡️

Berri AI is a python package that helps you quickly and easily deploy your LLM App from Colab/VSCode/etc. directly to production. Just install the package, import the function, and run deploy. At the end of the deploy (~10-15mins), you will get:

1. 🎉 A web app to interact with your agent 👉 [example](https://chat.berri.ai/aHR0cHM6Ly9hZ2VudC1yZXBvLTExN2Y0ZmM2LTkyZmMtNDdmNS05NDMyLWJlMDEzOTA2MzRhMy03NzM2MC00OXloLnplZXQtdGVhbS1pc2hhYW4tamFmZi56ZWV0LmFwcC8=) (hint: ask the agent if you can accept international payments from india)
2. 😱 An endpoint you can query 👉 `https://agent-repo-35aa2cf3-a0a1-4cf8-834f-302e5b7fe07e-45247-8aqi.zeet-team-ishaan-jaff.zeet.app/langchain_agent?query="who is obama?"`

![ezgif com-gif-maker(1)](https://user-images.githubusercontent.com/17561003/216242793-a5cc6887-3f02-4421-ae2d-1cd0df11c342.gif)

### [Demo Video / Walkthrough](https://www.loom.com/share/fd4375b4a77f4ea7802369cb06a16d43)

## 🤓 Usage

There are 5 major ways you can use Berri

1. Pipelines: Best way to get started. Pipelines let you spin up an LLM App in 2-lines of code.
2. GPT-Index: If you're writing an LLM app with the primary method of interaction being gpt-index's .query() function.
3. Langchain: If you're writing an LLM app with the primary method of interaction being Langchain's 'initialize_agent' or 'AgentExecutor()' functions
4. Wrapper functions: For more complex use-cases. If you're taking a user query and doing multiple things (LLM calls, api calls, etc.) with it, you can put them in a wrapper function and pass the wrapper function to Berri.
5.

### 👷 Pipelines

Today we support 2 pipelines:

- `docQAPipeline`: This lets you paste a url link to your documentation and get a shareable web app to use it, in 15mins. We'll handle the chunking, vectorizing, agent initialization, deployment for you.

1. Install the package:

   ```
   pip install berri-ai
   ```

2. Import the deploy method:

   ```
   from berri_ai import docQAPipeline
   ```

3. Initiate the deployment by providing your email address:
   ```
   docQAPipeline(user_email, open_ai_key, input_url)
   # example docQAPipeline(user_email="krrishdholakia@gmail.com", open_ai_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", input_url="https://stripe.com/docs/india-accept-international-payments#TransactionPurposeCode")
   ```
   go [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) to get your openai api key

- `ComplexInformationQA`: This let's you pass an index from GPT-Index, and create a Langchain agent that answers complex questions (e.g.: "my order didn't arrive, even though I'd paid for express shipping") + provides references (i.e. documents that the agent looked at)

1. Install the package:

   ```
   pip install berri-ai
   ```

2. Import the ComplexInformationQA method:

   ```
   from berri_ai.ComplexInformationQA import ComplexInformationQA
   ```

3. Initiate the Complex Information Agent by providing your stored vector-index:
   ```
   index = GPTSimpleVectorIndex.load_from_disk("./doc_qa.json")
   CIQAgent = ComplexInformationQA(index)
   response = CIQAgent.run("my order didn't arrive, even though I'd paid for express shipping")
   ```
   Note: you will need to initialize your environment with your openai key (`os.environ["OPENAI_API_KEY"] = <openai_api_key>`)
   go [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) to get your openai api key

### GPT-Index

To use Berri AI w/ GPT-Index, follow these steps:

1. Install the package:

   ```
   pip install berri-ai
   ```

2. Import the deploy method:

   ```
   from berri_ai import deploy_gpt_index
   ```

3. Initiate the deployment by providing your email address:
   ```
   deploy_gpt_index(user_email=<your email>)
   # example deploy_gpt_index(user_email="ishaan@berri.com")
   ```
   Note: Today, Berri will only look for the '.query()' function. Let us know if there are other use-cases you would like us to support.

### Langchain

To use Berri AI w/ Langchain, follow these steps:

1. Install the package:

   ```
   pip install berri-ai
   ```

2. Import the deploy method:

   ```
   from berri_ai import deploy
   ```

3. Initiate the deployment by providing your email address:
   ```
   deploy(user_email=<your email>)
   # example deploy(user_email="ishaan@berri.com")
   ```
   Note: Today, berri will look for the initialize_agent() and AgentExecutor() functions in your code. If you're using another way of initializing your agent, let us know and we'll update the package to account for that.

Once deployment is complete, you will receive an email notification. The entire process usually takes 10-15 minutes.

### Wrapper Functions

To use Berri AI w/ Wrapper Functions, follow these steps:

1. Install the package:

   ```
   pip install berri-ai
   ```

2. Import the deploy method:

   ```
   from berri_ai import deploy_func
   ```

3. Initiate the deployment by providing your email address:
   ```
   deploy_func(user_email=<your email>, executing_function=<stringified name of your executing function>, test_str=<test_user_input_query>)
   # example deploy_func(user_email="krrishdholakia@gmail.com", executing_function="print_answer", test_str="what is ManimML?")
   ```

## 📚 Examples

1. [Berri LangChain Youtube Agent Example](https://colab.research.google.com/drive/1Do4Utp4crMSpPngDlZOXx30HFmKhtxIF?usp=sharing)
2. [Berri LangChain Search Agent Example](https://colab.research.google.com/drive/1cB-QfCaKBs2Npe58R60qf-II0wcsT6VQ?usp=sharing)
3. [Berri GPT Index + Langchain Document QA Example](https://colab.research.google.com/drive/1R4e4dd-qr4XxPbOGdAIj0ybtliSlO4Zm?usp=sharing)

## 🚨 Support

If you have any questions or need help using Berri AI, join the [Discord](https://discord.gg/KvG3azf39U) or Text/WhatsApp us @ +17708783106 📱.
