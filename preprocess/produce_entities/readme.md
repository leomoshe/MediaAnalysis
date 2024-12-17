$ cd /home/leo/Public/dev/MediaAnalysis/preprocess/produce_entities
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt --no-index -f ./wheels_ubuntu/ 

$ python app.py --path "/home/leo/Public/dev/MediaAnalysis/preprocess/data/History/output/srt/2.11.2023 Itaiy Buchris.srt"--output "/home/leo/Public/dev/MediaAnalysis/preprocess/data/History/output/entities"

$ python app.py --path "/home/leo/Public/dev/MediaAnalysis/preprocess/data/extern/master_chef/Pj71y-WhR74.srt" --output "/home/leo/Public/dev/MediaAnalysis/preprocess/data/extern/master_chef/entities"