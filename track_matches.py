import pickle
import networkx
import numpy
import cv2
import logging
import time
import argparse
import os,os.path
from opensfm import unionfind
def track_from_matches(path):
    uf = unionfind.UnionFind()
    sets = {}
    feature_from_file = {}
    for name in os.listdir(path):
        # images = cv2.imread(name)
        print name
        # name.split('.')[0] is 01 or 02 the type
        feature_path1 = os.path.join(os.path.join(args.dataset, 'features'),
                                     name.split('.')[0] + '.jpg.features.pkl.gz')
        feature_path2 = os.path.join(os.path.join(args.dataset, 'features'),
                                     name.split('.')[2] + '.jpg.features.pkl.gz')
        if not name.split('.')[0] + '.jpg' in feature_from_file:
            with open(feature_path1) as fout:
                points1, features1, color1 = pickle.load(fout)
            feature_from_file[name.split('.')[0] + '.jpg'] = [points1, features1, color1]

        if not name.split('.')[2] + '.jpg' in feature_from_file:
            with open(feature_path2) as fout:
                points2, features2, color2 = pickle.load(fout)
            feature_from_file[name.split('.')[2] + '.jpg'] = [points2, features2, color2]

        # print feature_path1
        with open(os.path.join(os.path.join(args.dataset, 'matches'), name)) as fout:
            matches_for_pair = pickle.load(fout)
        for match in matches_for_pair:
            uf.union((name.split('.')[0] + '.jpg', match[0]), (name.split('.')[2] + '.jpg', match[1]))
        print ('{} and {} have {} matches\n'.format(name.split('.')[0] + '.jpg',name.split('.')[2] + '.jpg',len(matches_for_pair)))
    for i in uf:
        if not uf[i] in sets:
            sets[uf[i]] = [i]
        else:
            sets[uf[i]].append(i)
    tracks = [t for t in sets.values() if len(t) >= 2]
    track_graph = networkx.Graph()
    for track_id, track in enumerate(tracks):
        for track_img_feaID in track:
            '''track_img_feaID[0] means image name, for example 01.jpg. And track_img_feaID[1] means feature ID'''
            track_graph.add_node(str(list(track_img_feaID)[0]), dipict=0)
            track_graph.add_node(track_id, dipict=1)# for another same thing, it will not add to the graph
            featureAll = feature_from_file[str(list(track_img_feaID)[0])]
            colorAll = featureAll[2]
            b, g, r = colorAll[track_img_feaID[1]]
            track_graph.add_edge(str(list(track_img_feaID)[0]), track_id, featureID=list(track_img_feaID)[1],
                                 feature_color=(r, g, b))
    return track_graph
def save_track(track_graph):
    try:
        if not os.path.isdir(os.path.join(args.dataset, 'tracks')):
            os.mkdir(os.path.join(args.dataset, 'tracks'))
        path = os.path.join(os.path.join(args.dataset, 'tracks'), 'track_graph.pkl.gz')
        with open(path, 'w') as fin:
            pickle.dump(track_graph, fin)
        return True
    except OSError:
        return False

def show_graph(track_graph):
    import matplotlib.pyplot as plt
    networkx.draw(track_graph)
    plt.show()

if __name__=='__main__':
    logging.debug('merge feature onto tracks')
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    start = time.time()
    parser = argparse.ArgumentParser(description='Plot matches between images')
    parser.add_argument('dataset',
                        help='path to the dataset to be processed')
    args = parser.parse_args()
    path = os.path.join(args.dataset, 'matches')
    # path_image = os.path.join(args.dataset, 'images')
    track_graph = track_from_matches(path)
    if save_track(track_graph):
        print ('Finish save track_graph')
        # show_graph(track_graph)
    else:
        print ('ERROR')


