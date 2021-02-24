# Where can we apply our graph based mixture VAE? 

## Binary Labels  
not hierarchical
Could use gaussian mixture with only two distributions.

github stargazers. users following other users (starring repos). bniary labels, is the repo web or ml?
https://snap.stanford.edu/data/github_stargazers.html

reddit threads and replies 
https://snap.stanford.edu/data/reddit_threads.html


## Social-based ego networks    :left_speech_bubble:
could be hierarchical. There is overlap between clusters
http://i.stanford.edu/~julian/pdfs/nips2012.pdf

https://snap.stanford.edu/data/ego-Facebook.html
https://snap.stanford.edu/data/ego-Gplus.html
https://snap.stanford.edu/data/ego-Twitter.html

hierarchical - (3) Circles should be allowed to overlap, and ‘stronger’ circles should be allowed to form
within ‘weaker’ ones, e.g. a circle of friends from the same degree program may form within a circle

" (4) We would like to leverage both profile information and
network structure in order to identify the circles. Ideally we would like to be able to pinpoint which
aspects of a profile caused a circle to form, so that the model is interpretable by the user."


## wikipedia networks   :scroll: 

## citations networks :page_with_curl:  
has several features. 
journal venues.
temporal.
has keywords 
not really hierarchical, except maybe for keywords under journal/publisher
https://www.aminer.org/citation


## bio networks (check snap tutorial)  :test_tube:

Human Disease Network 
https://www.pnas.org/content/104/21/8685

Yeast protein interaction network (used for link prediction, a little underwhelming, undirected and unweighted) 
http://snap.stanford.edu/deepnetbio-ismb/ipynb/Graph+Convolutional+Prediction+of+Protein+Interactions+in+Yeast.html

protein-protein interaction networks in general 

## temporal networks  :stopwatch: 

## Misc

road network http://networkrepository.com/road-euroroad.php


## resources 
http://networkrepository.com/  -  very cool graph data 
https://snap.stanford.edu/data/
https://www.aminer.org/    		- citation networks 
