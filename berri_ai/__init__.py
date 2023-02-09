__version__ = '0.16.5'
import ast 
import re
import os 
import traceback
import time
import pipreqs
import subprocess
import requests
import shutil
from mixpanel import Mixpanel
import uuid
from berri_ai.DocStore import DocStore 
from typing import Union, List, Optional
import json 

mp = Mixpanel("69c4620538e80373ae4ef8edb32ce5e3")

def send_files(user_email, template_name):
    url = f'https://berriserverv2.krrishdholakia.repl.co/berri_orchestrator?user_email={user_email}&template_name={template_name}'
    files_list = []
    
    for file in os.listdir("./berri_files"):
        if os.path.isdir(file):
          raise ValueError(f"🚨🚨 Deployment Error 📣: {file} is a folder, it can't be sent. Join us on Discord (https://discord.gg/KvG3azf39U) if this is causing you issues.")
        with open(os.path.join("./berri_files", file), 'rb') as f:
          files_list.append((file, f.read()))
            
    response = requests.get(url, files=files_list)
    return response.json()["message"]

def traverse_ast(tree_dict, code, tree, global_dict):
  for node in tree.body:
      if isinstance(node, ast.With):
        # print(dir(node.items[0]))
        # print("ast.dump(node.items[0]) ", ast.dump(node.items[0]))
        node_value_source = ast.get_source_segment(code, node)
        # print("ast.with value_source: ", node_value_source)
        # print("node.body: ", node.body)
        for child in node.body: 
          if isinstance(child, ast.Assign):
            value_source = ast.get_source_segment(code, child)
            # print("value of child node: ", value_source)
            # print("value_source: ", value_source)
            str_split = value_source.split("=", 1)
            key_val = str(str_split[0]).strip()
            if key_val in tree_dict: 
              if node_value_source == tree_dict[key_val]:
                continue
              else:
                raise KeyError("🚨🚨 Deployment Error 📣: The variable - " + key_val + ' has been initialized 2 times. Here are the instances: \n 1.' + tree_dict[key_val][:100] + '\n 2.' + value_source[:100])
            tree_dict[key_val] = node_value_source
      if isinstance(node, ast.Assign):
        value_source = ast.get_source_segment(code, node)
        # print("value_source: ", value_source)
        str_split = value_source.split("=", 1)
        key_val = str(str_split[0]).strip()
        value = str(str_split[1]).strip()
        if key_val in tree_dict: 
          if value_source == tree_dict[key_val]:
            continue
          else:
            raise KeyError("🚨🚨 Deployment Error 📣: The variable - " + key_val + ' has been initialized 2 times. Here are the instances: \n 1.' + tree_dict[key_val][:100] + '\n 2.' + value_source[:100])
        tree_dict[key_val] = value_source
      elif isinstance(node, ast.ClassDef):
          # print(node.name)
          key_val = node.name.strip()
          if key_val in tree_dict: 
            if ast.get_source_segment(code, node) == tree_dict[key_val]:
              continue
            else:
              raise KeyError("🚨🚨 Deployment Error 📣: The variable - " + key_val + ' has been initialized 2 times. Here are the instances: \n 1.' + tree_dict[key_val][:100] + '\n 2.' + value_source[:100])
          tree_dict[key_val] = ast.get_source_segment(code, node)
      elif isinstance(node, ast.FunctionDef):
          # print(node.name)
          key_val = node.name.strip()
          if key_val in tree_dict: 
            if ast.get_source_segment(code, node) == tree_dict[key_val]:
              continue
            else:
              raise KeyError("🚨🚨 Deployment Error 📣: The variable - " + key_val + ' has been initialized 2 times. Here are the instances: \n 1.' + tree_dict[key_val][:100] + '\n 2.' + value_source[:100])
          tree_dict[key_val] = ast.get_source_segment(code, node)
      elif isinstance(node, ast.Import):
          value_source = ast.get_source_segment(code, node)
          # print("value_source in import: ", value_source)
          for name in node.names:
            # print("name: ", name.name)
            key_val = name.name
            # if key_val in tree_dict: 
            #   if value_source == tree_dict[key_val]:
            #     continue
            #   else:
            #     raise KeyError(key_val + ' already exists in the dictionary: ' + tree_dict[key_val] + ' | youre trying to set it to: ' + value_source)
            tree_dict[name.name] = value_source
            if "." in name.name:
              split_names = name.name.split(".")[0]
              key_val = split_names
              # if key_val in tree_dict: 
              #   if value_source == tree_dict[key_val]:
              #     continue
              #   else:
              #     raise KeyError(key_val + ' already exists in the dictionary: ' + tree_dict[key_val] + ' | youre trying to set it to: ' + value_source)
              tree_dict[key_val] = value_source
      elif isinstance(node, ast.ImportFrom):
          value_source = ast.get_source_segment(code, node)
          for name in node.names:
            key_val = name.name
            # if key_val in tree_dict: 
            #   if value_source == tree_dict[key_val]:
            #     continue
            #   else:
            #     raise KeyError(key_val + ' already exists in the dictionary: ' + tree_dict[key_val] + ' | youre trying to set it to: ' + value_source)
            tree_dict[name.name] = value_source

def check_requirements(package):
    with open('./berri_files/requirements.txt', 'r') as file:
        content = file.read()
        if package not in content:
            with open('./berri_files/requirements.txt', 'a') as file2:
                file2.write(package)

def get_dependencies(code_segment_list, global_dict):
    # Run function in a sandbox and catch ImportErrors
    dep_modules = None
    # print("new list")
    bool_val = True
    i = 0
    while bool_val:
      if i >= 20:
        raise Exception("there is an issue in the loop")
      # print("in while loop")
      dep_modules = []
      try:
        for code_segment in code_segment_list:
          # exec(print(dir()))
          exec(code_segment, global_dict)
          # func()  # Try to run function in the sandbox
        bool_val = False
      except ModuleNotFoundError as e:
        text = e.args[0]
        match = re.search(r"'(.*)'", text)
        if match:
            package_name = match.group(1)
            check_requirements(package_name)
            # print("module not found in dep exec: ", package_name)
            install_statements = []
            install_statements.append("import subprocess")
            install_statements.append(str("""subprocess.call(['pip', 'install','""" + package_name + "'])"))
            for install_statement in install_statements:
              exec(install_statement)
              # print("install_statement: ", install_statement)
            # print("below module package install bool val: ", bool_val)
      except Exception as e:
        # print(e)
        # traceback.print_exc()
        if hasattr(e, 'name'):
          # print("e.name: ", e.name)
          dep_modules.append(e.name)  # Add module that caused error
          bool_val = False
        else:
            # print(e.args)
            text = e.args[0]
            # print("text: ", text)
            pattern = r"pip install (\w+)"
            # print(type(text))
            # print(isinstance(text, list))
            # print(len(text))
            if isinstance(text, list):
              text = str(text[0])
              # print("text cleaned up: ", text)
            match = re.search(pattern, text)
            if match:
              # print("validation error here")
              package_name = match.group(1)
              # print("Package name to install:", package_name)
              # print("below package install bool val: ", bool_val)
              install_statements = []
              install_statements.append("import subprocess")
              install_statements.append(str("""subprocess.call(['pip', 'install','""" + package_name + "'])"))
              for install_statement in install_statements:
                exec(install_statement)
            else:
              match = re.search(r"'(.*)'", text)
              if match:
                  # print("dependency module error here")
                  quoted_text = match.group(1)
                  # print(quoted_text)
                  dep_modules.append(quoted_text)
                  bool_val = False
      # print("bool val: ", bool_val)
    return dep_modules

def copy_files():
  current_directory = os.getcwd()
  if not os.path.exists(current_directory + '/berri_files'):
      os.mkdir(current_directory + '/berri_files')
  list_of_restricted_dirs = ['berri_files', 'sample_data', 'drive', '.config', '__pycache__', '.ipynb_checkpoints']
  for subdir, dirs, files in os.walk(current_directory):
    for file in files:
      if (file != 'sample_data' and file != 'drive') and (subdir == current_directory):
        # print("file: ", file)
        shutil.copy(file, current_directory + '/berri_files')
    for dir in dirs:
      if (dir not in list_of_restricted_dirs) and (subdir == current_directory):
        # print("dir: ", dir)
        shutil.copytree(dir, current_directory + '/berri_files/' + dir)

def run_loop(environment_list, code_list, tree_dict, global_dict):
  code_segment_list = None
  for i in range(20):
    code_segment_list = environment_list + code_list 
    # print("code_segment_list: ", code_segment_list)
    # print(i)
    dependencies = get_dependencies(code_segment_list, global_dict)
    # print("dependencies: ", dependencies)
    if len(dependencies) == 0:
      break
    for dependency in dependencies:
      # print("dependency: ", dependency)
      code = tree_dict[dependency]
      # print("dependency parent_dependency: ", parent_dependency)
      code_list.insert(0, code)
  return code_segment_list


def save_requirements(path, requirements):
  # print("reaches save requirements")
  subprocess.run(["pipreqs", "--mode", "no-pin", path])
  with open('./berri_files/requirements.txt', 'r') as f:
    existing_reqs = f.readlines()
    existing_reqs = [req.strip().split("=")[0] for req in existing_reqs]

  with open('./berri_files/requirements.txt', 'a') as f:
    if len(requirements) > 0:
      for requirement in requirements:
        for r in requirement:
          tmp_req = r.split("=")[0]
          if tmp_req not in existing_reqs:
              f.write(tmp_req + '\n')
          else:
              # print(f"{tmp_req} is already in requirements.txt")
              continue

def get_requirements(line):
  line_split = line.split(' && ')
  requirements = []

  for line in line_split:
    line_split_2 = line.split(' ')
    package = line_split_2[-1]
    requirements.append(package)
  
  return requirements

def install_requirements():
  with open('./berri_files/requirements.txt', 'r') as f:
    existing_reqs = f.readlines()
    existing_reqs = [req.strip().split("=")[0] for req in existing_reqs]

  for package_name in existing_reqs:
    install_statements = []
    install_statements.append("import subprocess")
    install_statements.append(str("""subprocess.call(['pip', 'install','""" + package_name + "'])"))
    for install_statement in install_statements:
      exec(install_statement)

# def read_file_copy_drive_files(line):
#   # Check if the line contains a path to a file or folder
#   path = re.search(r'"([^"]*drive[^"]*)"', line)
#   if path: 
#       if os.path.exists(path.group(1)):
#         # Copy the file/folder to the berri_files folder
#         new_filepath = None
#         if os.path.isdir(path.group(1)):
#           for file in os.listdir(path.group(1)): 
#             shutil.copy(os.path.join(path.group(1), file), 'berri_files')
#             new_filepath = file
#         else:
#             shutil.copy(path.group(1), 'berri_files')
#             new_filepath = file
#         # Update the line with the new filepath
#         if new_filepath:
#           line = re.sub(r'"([^"]*)"', '"' + new_filepath + '"', line)     
#   return line 



def docQAPipeline(user_email: str, openai_ai_key: str, input_url_or_list: Union[str, List[str]], language: Optional[str] = None):
  from gpt_index import SimpleWebPageReader, GPTSimpleVectorIndex, PromptHelper
  import os
  try:
    print("Begun deployment..")
    print("🚨 Hit an error? let us know in the Discord (https://discord.gg/KvG3azf39U).")
    print("🐍 Chunking + Vectorizing + Storing your url data, this might take 1-2 minutes.")

    try:
      mp.track(str(uuid.uuid4()), "package.start.berri.docQAPipeline()", {
        'UserEmail': user_email
      })
    except:
      print("MP error")

    if isinstance(input_url_or_list, str):
      # code to process single URL
      os.environ["OPENAI_API_KEY"] = openai_ai_key
      # set maximum input size
      max_input_size = 4096
      # set number of output tokens
      num_output = 256
      # set maximum chunk overlap
      max_chunk_overlap = 20
      prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
      documents = SimpleWebPageReader(html_to_text=True).load_data([input_url])
      index = GPTSimpleVectorIndex(documents, prompt_helper=prompt_helper)
      if not os.path.exists('./berri_files/'):
        os.mkdir("./berri_files/")
      index.save_to_disk("./berri_files/doc_qa.json")
    elif isinstance(input_url_or_list, list):
      # code to process list of documents
      documentsData = []
      for item in input_url_or_list:
        with open(item, "r") as f:
          documentData = f.read()
          documentsData.append(documentData)
      if language == None:
        raise RuntimeError(f"🚨🚨 Runtime Error 📣: need to specify if language in docs is 'english' or 'portugese' if you pass in a list of doc files")
      DocStore(documentsData, language)
      credentials = {"openai_api_key": openai_ai_key}
      with open("./berri_files/credentials.json", "w") as f:
        json.dump(credentials, f)
    endpoint = "https://" + send_files(user_email, "berri_backend_pipeline_server_template")
    print("🚧 Currently deploying to [NOT READY YET] 👉 " + endpoint)
    print("⌛️ It'll be ready in 15 mins. We'll email you  @ " + user_email)
  except Exception as e: 
    print(e)
    traceback.print_exc()
    print("🚨🚨 Deployment Error 📣: There was an error deploying your project. Join us on Discord (https://discord.gg/KvG3azf39U) and we'll fix this for you.")
    try:
      mp.track(str(uuid.uuid4()), "package.error.berri.gpt_index_deploy()", {
        'UserEmail': user_email,
        'Error': traceback.print_exc()
      })
    except:
      print("MP error")
  print("=====================")
  print("Got feedback? Text/WhatsApp us 👉 +17708783106")


def deploy_func(user_email: str, executing_function, test_str: str):
  from google.colab import _message
  try:
    print("Begun deployment..")
    print("🚨 Hit an error? let us know in the Discord (https://discord.gg/KvG3azf39U).")
    print("🐍 Converting notebook to python and generating requirements.txt, this might take 1-2 minutes.")

    try:
      mp.track(str(uuid.uuid4()), "package.start.berri.deploy_func()", {
        'UserEmail': user_email
      })
    except:
      print("MP error")
    # assume you're in a google colab 
    if not os.path.exists('./berri_files/'):
      os.mkdir("./berri_files/")

    copy_files() # copies all local non-drive/sample_data files and folders into berri_files

    # Obtain the notebook JSON as a string
    notebook_json_string = _message.blocking_request('get_ipynb', request='', timeout_sec=5)

    # save to temporary file
    lines = []
    requirements = []
    for cell in notebook_json_string["ipynb"]["cells"]:
      if cell["cell_type"] == "code":
        for line in cell["source"]:
          if line.startswith("!pip install"):
            requirements.append(get_requirements(line))
            # continue
          elif not line.startswith("!"):
            lines.append(line)
    
    f = open("./berri_files/agent_code.py", "w")
    for line in lines:
      # line = read_file_copy_drive_files(line)
      f.write(line + "\n")
    f.close()
    
    # save the requirements to a requirements.txt file 
    save_requirements("./berri_files", requirements)

    with open("./berri_files/agent_code.py") as f:
        lines = f.readlines()
    
    with open("./berri_files/agent_code.py") as f:
        code = f.read()

    tree = ast.parse(code)
    tree_dict = {}
    global_dict = {}
    # traverse the file and create a dictionary
    traverse_ast(tree_dict, code, tree, global_dict)
    # print("global_dict: ", global_dict)
    # print("tree_dict: ", tree_dict)


    # set the executing line
    agent_executing_line = "" + str(executing_function) + "('" + test_str+ "')"
    # print("agent_executing_line: ", agent_executing_line)
    # find the import statements
    import_statements = []
    for line in lines:
      if "google.colab" in line or "drive.mount('/content/drive')" in line:
        continue
      elif "import" in line:
        import_statements.append(line)

    # run_loop(import_statements, tree_dict, global_dict)
    # print(import_statements)

    parent_dependencies = []
    
    for key in tree_dict:
      if "os" in key:
        parent_dependencies.append(tree_dict[key])
    
    # print("parent_dependencies: ", parent_dependencies)
    
    parent_dependencies = run_loop(import_statements, parent_dependencies, tree_dict, global_dict)

    # print("updated parent dependencies: ", parent_dependencies)
        
    implementation_code = [agent_executing_line]
    environment_setup_list = import_statements + parent_dependencies
    # print("running main code now")
    install_requirements()
    all_up_code = run_loop(environment_setup_list, implementation_code, tree_dict, global_dict)

    # print("all_up_code: ", all_up_code)
    # print("executing_function: ", executing_function)
    with open("./berri_files/agent_code.py", "w") as f:
      for code_segment in all_up_code:
        if executing_function in code_segment:
          # print("true")
          code_segment = code_segment.replace(executing_function, "agent").strip()
        f.write(code_segment + "\n")

    print("😱 Building docker image.. this might take 1-2 minutes")
    endpoint = "https://" + send_files(user_email, "berri_backend_server_template")

    print("🚧 Currently deploying to [NOT READY YET] 👉 " + endpoint)
    print("⌛️ It'll be ready in 15 mins. We'll email you  @ " + user_email)
  except Exception as e:
    print(e)
    traceback.print_exc()
    print("🚨🚨 Deployment Error 📣: There was an error deploying your project. Join us on Discord (https://discord.gg/KvG3azf39U) and we'll fix this for you.")
    try:
      mp.track(str(uuid.uuid4()), "package.error.berri.gpt_index_deploy()", {
        'UserEmail': user_email,
        'Error': traceback.print_exc()
      })
    except:
      print("MP error")
  print("=====================")
  print("Got feedback? Text/WhatsApp us 👉 +17708783106")

def deploy_gpt_index(user_email: str):
  from google.colab import _message
  try:
    print("Begun deployment..")
    print("🚨 Hit an error? let us know in the Discord (https://discord.gg/KvG3azf39U).")
    print("🐍 Converting notebook to python and generating requirements.txt, this might take 1-2 minutes.")

    try:
      mp.track(str(uuid.uuid4()), "package.start.berri.gpt_index_deploy()", {
        'UserEmail': user_email
      })
    except:
      print("MP error")
    # assume you're in a google colab 
    if not os.path.exists('./berri_files/'):
      os.mkdir("./berri_files/")

    copy_files() # copies all local non-drive/sample_data files and folders into berri_files

    # Obtain the notebook JSON as a string
    notebook_json_string = _message.blocking_request('get_ipynb', request='', timeout_sec=5)

    # save to temporary file
    lines = []
    requirements = []
    for cell in notebook_json_string["ipynb"]["cells"]:
      if cell["cell_type"] == "code":
        for line in cell["source"]:
          if line.startswith("!pip install"):
            requirements.append(get_requirements(line))
            # continue
          elif not line.startswith("!"):
            lines.append(line)
    
    f = open("./berri_files/agent_code.py", "w")
    for line in lines:
      if ".query(" in line:
        # print("line where query was found: ", line)
        # get the variable name
        if "=" in line:
          initialization_line = line.split("=", 1)
        else:
          initialization_line = line
        # print("original_agent_name: ", original_agent_name)
        # replace with new name 
        prev_name = initialization_line[1].split(".query")[0].strip()
        reinitialize_agent = "agent = " + prev_name
        f.write(reinitialize_agent + "\n")
        line = initialization_line[1].replace(prev_name, "agent").strip()
        # print(initialization_line)
        f.write(line + "\n")
      else:
        # line = read_file_copy_drive_files(line)
        f.write(line + "\n")
    f.close()
    
    # save the requirements to a requirements.txt file 
    save_requirements("./berri_files", requirements)

    with open("./berri_files/agent_code.py") as f:
        lines = f.readlines()
    
    with open("./berri_files/agent_code.py") as f:
        code = f.read()

    tree = ast.parse(code)
    tree_dict = {}
    global_dict = {}
    # traverse the file and create a dictionary
    traverse_ast(tree_dict, code, tree, global_dict)
    # print("global_dict: ", global_dict)
    # print("tree_dict: ", tree_dict)

    # find the executing line
    agent_executing_line = "agent.query("
    # find the import statements
    import_statements = []
    for line in lines:
      if agent_executing_line in line:
        # print(line)
        agent_executing_line = line.strip() # find the executing line 
        # print("agent_executing_line: ", agent_executing_line)
      elif "google.colab" in line or "drive.mount('/content/drive')" in line:
        continue
      elif "import" in line:
        import_statements.append(line)

    # run_loop(import_statements, tree_dict, global_dict)
    # print(import_statements)

    parent_dependencies = []
    
    for key in tree_dict:
      if "os" in key:
        parent_dependencies.append(tree_dict[key])
    
    # print("parent_dependencies: ", parent_dependencies)
    
    parent_dependencies = run_loop(import_statements, parent_dependencies, tree_dict, global_dict)

    # print("updated parent dependencies: ", parent_dependencies)
        
    implementation_code = [agent_executing_line]
    environment_setup_list = import_statements + parent_dependencies
    # print("running main code now")
    all_up_code = run_loop(environment_setup_list, implementation_code, tree_dict, global_dict)

    # print("all_up_code: ", all_up_code)

    with open("./berri_files/agent_code.py", "w") as f:
      for code_segment in all_up_code:
        f.write(code_segment + "\n")

    print("😱 Building docker image.. this might take 1-2 minutes")
    endpoint = "https://" + send_files(user_email, "berri_backend_server_template")

    print("🚧 Currently deploying to [NOT READY YET] 👉 " + endpoint)
    print("⌛️ It'll be ready in 15 mins. We'll email you  @ " + user_email)
  except Exception as e:
    print(e)
    traceback.print_exc()
    print("🚨🚨 Deployment Error 📣: There was an error deploying your project. Join us on Discord (https://discord.gg/KvG3azf39U) and we'll fix this for you.")
    try:
      mp.track(str(uuid.uuid4()), "package.error.berri.gpt_index_deploy()", {
        'UserEmail': user_email,
        'Error': traceback.print_exc()
      })
    except:
      print("MP error")
  print("=====================")
  print("Got feedback? Text/WhatsApp us 👉 +17708783106")

def deploy(user_email: str):
  from google.colab import _message
  try:
    print("Begun deployment..")
    print("🚨 Hit an error? let us know in the Discord (https://discord.gg/KvG3azf39U).")
    print("🐍 Converting notebook to python and generating requirements.txt, this might take 1-2 minutes.")
    try:
      mp.track(str(uuid.uuid4()), "package.start.berri.deploy()", {
        'UserEmail': user_email
      })
    except:
      print("MP error")

    # assume you're in a google colab 
    if not os.path.exists('./berri_files/'):
      os.mkdir("./berri_files/")

    copy_files() # copies all local non-drive/sample_data files and folders into berri_files

    # Obtain the notebook JSON as a string
    notebook_json_string = _message.blocking_request('get_ipynb', request='', timeout_sec=5)

    # save to temporary file
    lines = []
    requirements = []
    for cell in notebook_json_string["ipynb"]["cells"]:
      if cell["cell_type"] == "code":
        for line in cell["source"]:
          if line.startswith("!pip install"):
            requirements.append(get_requirements(line))
            # continue
          elif not line.startswith("!"):
            lines.append(line)
    
  # get the variable name
  # replace with new name 
    original_agent_name = None
    f = open("./berri_files/agent_code.py", "w")
    for line in lines:
      if original_agent_name and original_agent_name + ".run(" in line: # if it exists and is being executed, replace that line
        line = line.replace(original_agent_name + ".run(", "agent.run(")
        f.write(line + "\n")
      if "initialize_agent(" in line:
        initialization_line = line.split("=", 1)
        original_agent_name = initialization_line[0].strip() # get the original agent variable name
        # print("original_agent_name: ", original_agent_name)
        initialization_line = "agent = " + initialization_line[1]
        # print(initialization_line)
        f.write(initialization_line + "\n")
      else:
        # line = read_file_copy_drive_files(line)
        f.write(line + "\n")
    f.close()
    
    # save the requirements to a requirements.txt file 
    save_requirements("./berri_files", requirements)

    # if len(requirements) > 0: 
    #   with open('./berri_files/requirements.txt', 'a') as f:
    #     for requirement in requirements:
    #       for r in requirement:
    #         print("requirement: ", r)
    #         f.write("\n" + r + '\n')

    with open("./berri_files/agent_code.py") as f:
        lines = f.readlines()
    
    with open("./berri_files/agent_code.py") as f:
        code = f.read()

    tree = ast.parse(code)
    tree_dict = {}
    global_dict = {}
    # traverse the file and create a dictionary
    traverse_ast(tree_dict, code, tree, global_dict)
    # print("global_dict: ", global_dict)
    # print("tree_dict: ", tree_dict)

    # find the executing line
    agent_executing_line = "agent.run("
    # find the import statements
    import_statements = []
    for line in lines:
      if agent_executing_line in line:
        # print(line)
        agent_executing_line = line.strip() # find the executing line 
      elif "google.colab" in line or "drive.mount('/content/drive')" in line:
        continue
      elif "import" in line:
        import_statements.append(line)

    # run_loop(import_statements, tree_dict, global_dict)
    # print(import_statements)

    parent_dependencies = []
    
    for key in tree_dict:
      if "os" in key:
        parent_dependencies.append(tree_dict[key])
    
    # print("parent_dependencies: ", parent_dependencies)
    
    parent_dependencies = run_loop(import_statements, parent_dependencies, tree_dict, global_dict)

    # print("updated parent dependencies: ", parent_dependencies)
        
    implementation_code = [agent_executing_line]
    environment_setup_list = import_statements + parent_dependencies
    # print("running main code now")
    all_up_code = run_loop(environment_setup_list, implementation_code, tree_dict, global_dict)

    # print("all_up_code: ", all_up_code)

    with open("./berri_files/agent_code.py", "w") as f:
      for code_segment in all_up_code:
        f.write(code_segment + "\n")

    print("😱 Building docker image.. this might take 1-2 minutes")
    endpoint = "https://" + send_files(user_email, "berri_backend_server_template")

    print("🚧 Currently deploying to [NOT READY YET] 👉 " + endpoint)
    print("⌛️ It'll be ready in 15 mins. We'll email you  @ " + user_email)
  except Exception as e:
    print(e)
    traceback.print_exc()
    print("🚨🚨 Deployment Error 📣: There was an error deploying your project. Join us on Discord (https://discord.gg/KvG3azf39U) and we'll fix this for you.")
    try:
      mp.track(str(uuid.uuid4()), "package.error.berri.deploy()", {
        'UserEmail': user_email,
        'Error': traceback.print_exc()
      })
    except:
      print("MP error")
  print("=====================")
  print("Got feedback? Text/WhatsApp us 👉 +17708783106")