# LangCoop
🏆 CVPR 2025 MEIS Workshop Best Paper Award

This repo is the official implementation of "LangCoop: Collaborative Driving with Language".


[![Paper](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)](https://www.arxiv.org/pdf/2504.13406) [![Project Page](https://img.shields.io/badge/Project-Page-1f72ff.svg)](https://xiangbogaobarry.github.io/LangCoop/) [![Code](https://img.shields.io/badge/GitHub-Code-black.svg)](https://github.com/taco-group/LangCoop)


## Env Setup
We provide two options for setting up the environment:

1. Step-by-step manual installation (recommended for Ubuntu 22.04, CUDA 11.6)
2. Docker container (for easier setup across different hardware) - `docker pull myopensource/langcoop:v1.0`

### Step 1: Basic Installation
Get code and create pytorch environment. (The code is best tested in Ubuntu 22.04, CUDA 11.6)
```Shell
git clone https://github.com/taco-group/LangCoop.git
conda create --name LangCoop python=3.8 cmake=3.22.1
conda activate LangCoop
conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.6 -c pytorch -c nvidia
conda install cudnn -c conda-forge

cd LangCoop
python -m pip install -r opencood/requirements.txt
python -m pip install -r simulation/requirements.txt
python -m pip install -r openemma_requirements.txt

#Install spconv
python -m pip install spconv-cu116

# Set up opencood
python setup.py develop
python opencood/utils/setup.py build_ext --inplace  # Bbx IOU cuda version compile

# Install pypcd
cd .. # go to another folder
git clone https://github.com/klintan/pypcd.git
cd pypcd
python -m pip install python-lzf
python setup.py install
cd ..

# install efficientNet
python -m pip install efficientnet_pytorch==0.7.0

```

### Step 2: Download and setup CARLA 0.9.10.1.
Carla code is only tested in CARLA 0.9.10.1 which requires python 3.7. So please open another environment with python 3.7 to install carla.
```Shell
conda deactivate
conda create --name LangCoopCarla python=3.7
conda activate LangCoopCarla
python -m pip install setuptools==41
chmod +x simulation/setup_carla.sh
./simulation/setup_carla.sh
easy_install carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg
mkdir external_paths
ln -s ${PWD}/carla/ external_paths/carla_root
# If you already have a Carla, just create a soft link to external_paths/carla_root
```
Note: we choose the setuptools==41 to install because this version has the feature `easy_install`. After installing the carla.egg you can install the lastest setuptools to avoid No module named distutils_hack.

## How to config?
We support both local VLM deployment and API-based providers, as long as the requests are compatible with the OpenAI format.

### Using API provider (e.g. OpenRouter)
#### step1: Add Your API key
replace your api key in `vlmdrive/api_keys/api_key.txt`
```bash
<put-your-api-key-here>
```

#### step2: Update the Model Config
Modify vlmdrive/vlm/hypes_yaml to match the api_base_url and api_model_name:
```yaml
model: 
  type: VLMPlannerSpeedCurvature # options: VLMPlannerSpeedCurvature, VLMPlannerWaypoint, VLMPlannerControl
  name: api
  api_model_name: anthropic/claude-3.7-sonnet
  api_base_url: https://openrouter.ai/api/v1
  api_key: vlmdrive/api_key.txt
```

#### step3: Configure Heterogeneous Agents
Please prepare configuration files for each model you intend to use and place them in the `vlmdrive/vlm/hypes_yaml` directory. Each model requires a corresponding configuration file. You can refer to our template to create your own configurations.

Then, for example in `vlmdrive/agent/hypes_yaml/speed_curvature_CoT_concise_image_intent_2agent_claude.yaml`, list all the configured models under the heter section to specify the available heterogeneous models for testing.
```yaml
simulation:
    ego_num: 2                     # number of communicating drivable ego vehicles
    skip_frames: 4                 # frame gap before a new driving control signal is generated

heter:
    avail_heter_planner_configs: 
        - "vlmdrive/hypes_yaml/api_vlm_drive_speed_curvature_qwen2.5-72b-awq.yaml"      # 0
        - "vlmdrive/hypes_yaml/api_vlm_drive_speed_curvature_qwen2.5-3b-awq.yaml"       # 1
        - "vlmdrive/hypes_yaml/api_vlm_drive_speed_curvature_qwen2.5-7b-awq.yaml"       # 2
        - "vlmdrive/vlm/hypes_yaml/waypoints.yaml"                                      # 3
    ego_planner_choice: [0, 0] # available indexes above
```

To properly configure heterogeneous agents:

1. Set the correct number of ego vehicles `ego_num`.
2. Add all available model configurations to the `avail_heter_planner_configs` list.
3. Define the `ego_planner_choice`, where each index corresponds to an ego vehicle and specifies the model it adopts from `avail_heter_planner_configs`.

#### step4: Update the Evaluation Script
Modify scripts/eval_driving_vlm.sh to ensure EGO_NUM is set correctly:
```bash
export EGO_NUM=2
```

### [Optional] Using Local Deployed Models
We use vLLM to deploy and run local models. Here are the detailed deployment steps:

#### step1: Environment Setup
First, create and configure the vLLM environment:
```bash
conda create -n vllm python=3.12 -y
conda activate vllm
git clone https://github.com/vllm-project/vllm.git
cd vllm
VLLM_USE_PRECOMPILED=1 pip install --editable .
```

#### step2: Download Models
Create a model storage directory and download the required models:
```bash
mkdir vlm_models
huggingface-cli download Qwen/Qwen2.5-VL-3B-Instruct-AWQ --local-dir vlm_models/Qwen/Qwen2.5-VL-3B-Instruct-AWQ
```

#### step3: Start Services
You can choose to start services with different model sizes. Here are two examples:

Start 3B model:
```bash
CUDA_VISIBLE_DEVICES=2 python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-VL-3B-Instruct-AWQ \
    --download-dir /other/vlm_models \
    --host 0.0.0.0 \
    --port 8000 \
    --dtype float16 \
    --gpu-memory-utilization 0.7 \
    --max-model-len 8192 \
    --trust-remote-code
```

Start 7B model:
```bash
CUDA_VISIBLE_DEVICES=3 python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-VL-7B-Instruct-AWQ \
    --download-dir /other/vlm_models \
    --host 0.0.0.0 \
    --port 8001 \
    --dtype float16 \
    --gpu-memory-utilization 0.7 \
    --max-model-len 8192 \
    --trust-remote-code
```

#### step4: Configuration File Modification
When using locally deployed models, modify the configuration file `LangCoop/vlmdrive/vlm/hypes_yaml/api_vlm_drive_speed_curvature_qwen2.5-3b-awq.yaml`:

```yaml
  api_model_name: Qwen/Qwen2.5-VL-3B-Instruct-AWQ
  api_base_url: http://localhost:8000/v1
  api_key: dummy_key
```

#### step5: Test Service
You can test if the service is running properly using the following command:
```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-VL-3B-Instruct-AWQ",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "max_tokens": 100
    }'
```

### Controller Config
We support three controllers:
- VLMControllerControl
- VLMControllerSpeedCurvature
- VLMControllerWaypoint

Configurations are available in `vlmdrive/controller/hypes_yaml`.

(TBM)

## Experiments

#### (option): launch local VLLM
For heterogeneous testing, multiple VLLM services must be started, each on a different port. For example, ensure that the model’s port matches the configuration in `vlmdrive/vlm/hypes_yaml/api_vlm_drive_speed_curvature_qwen2-2b-awq.yaml`.

```bash
CUDA_VISIBLE_DEVICES=3 python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-VL-7B-Instruct-AWQ \
    --download-dir /other/vlm_models \
    --host 0.0.0.0 \
    --port 8001 \ # different model should have different port
    --dtype float16 \
    --gpu-memory-utilization 0.7 \
    --max-model-len 8192 \
    --trust-remote-code
```

### Run close-loop evaluation
#### step1: launch Carla v0.9.10.1
```Shell
CUDA_VISIBLE_DEVICES=0 ./external_paths/carla_root/CarlaUE4.sh --world-port=2002 -prefer-nvidia  # Please make sure world-port matches the Carla_port=xxxx in the bash file.
```
Ensure that the port matches the configuration in `bash_files/testing/*`.

Please make sure `world-port` matches the `Carla_port=xxxx` in the bash file.

#### step2: run exp
```bash
bash bash_files/testing/speed_curvature_CoT_concise_image_intent_2agent.sh
```
You can find logs and results under `results/`

Aagin, please make sure that `Carla_port=xxxx` matches the Carla `--world-port=xxxx`

## Running with the Provided Docker Image
The code is located in ~/langcoop/. To ensure you have the latest version, pull updates or mount a fresh clone when launching the container. You can run CARLA and VLLM externally as long as the necessary ports are exposed.

Addtionally, ensure the `shm-size` is large (ideally matching system memory):
```bash
docker run myopensource/langcoop:v1.0 -it --shm-size=128g --network host 
```

For additional details, please refer to our documentation or open an issue in the repository.

## Acknowledgement

We build our framework on top of `V2XVerse`, please refer to the repo `https://github.com/CollaborativePerception/V2Xverse`
