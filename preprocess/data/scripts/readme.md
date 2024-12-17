$ cd /home/leo/Public/dev/MediaAnalysis/preprocess/data/90142_2022
$ cp -r tsrt tsrt_01
$ cd tsrt_01/
$ find . -type f -name "*.tsrt.csv" -exec sed -i 's|http://prsecsp19web1:8501?src|http://prsecspma?src|g' {} \;
$ sed -i 's/\(&tsrt=History\\\)output\\/\1/g' /home/leo/Public/dev/MediaAnalysis/preprocess/data/History/output/tsrt/*.tsrt.csv




## Postprocess
$ sudo mkdir /home/temp/90142_2022/
$ sudo mkdir /home/temp/90142_2022/tsrt
$ sudo mv /home/leo/Public/dev/MediaAnalysis/service/data/90142_2022/tsrt/* /home/temp/90142_2022/tsrt/

Copy to manat

Destination:
prSecSp19Web1
D:\Projects\MediaAnalysisViewer\tsrt\90142_2022
prsecspma
D:\projects\MediaAnalysis\MediaAnalysisViewer\tsrt\90142_2022
