$ cd /home/leo/Public/dev/MediaAnalysis/preprocess/process_tsrt
$ source .venv/bin/activate

# set media_path_replace in app.json
$ python app.py --path "/home/leo/Public/dev/MediaAnalysis/preprocess/data/History/output/entities/2.11.2023 Itaiy Buchris.entities.csv"--output "/home/leo/Public/dev/MediaAnalysis/preprocess/data/History/output/tsrt"
$ python app.py --path "/home/leo/Public/dev/MediaAnalysis/preprocess/data/entities/extern/master_chef/Pj71y-WhR74.entities.csv" --tsrt_path "History\\" --output "/home/leo/Public/dev/MediaAnalysis/preprocess/data/extern/master_chef/tsrt"