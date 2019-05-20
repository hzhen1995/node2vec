import argparse
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import node2vec
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import Word2Vec
from gensim.models import KeyedVectors


def parse_args():

	parser = argparse.ArgumentParser(description="Run node2vec.")

	parser.add_argument('--input', nargs='?', default='graph/karate.edgelist', help='Input graph path')

	parser.add_argument('--output', nargs='?', default='emb/karate.emb', help='Embeddings path')

	parser.add_argument('--dimensions', type=int, default=128, help='Number of dimensions. Default is 128.')

	parser.add_argument('--walk-length', type=int, default=80, help='Length of walk per source. Default is 80.')

	parser.add_argument('--num-walks', type=int, default=10, help='Number of walks per source. Default is 10.')

	parser.add_argument('--window-size', type=int, default=10, help='Context size for optimization. Default is 10.')

	parser.add_argument('--iter', default=1, type=int, help='Number of epochs in SGD')

	parser.add_argument('--workers', type=int, default=8, help='Number of parallel workers. Default is 8.')

	parser.add_argument('--p', type=float, default=1, help='Return hyperparameter. Default is 1.')

	parser.add_argument('--q', type=float, default=1, help='Inout hyperparameter. Default is 1.')

	parser.add_argument('--weighted', dest='weighted', action='store_true', help='Boolean specifying weighted. Default is weighted.')
	parser.add_argument('--unweighted', dest='unweighted', action='store_false')
	parser.set_defaults(weighted=False)

	parser.add_argument('--directed', dest='directed', action='store_true', help='Graph is (un)directed. Default is undirected.')
	parser.add_argument('--undirected', dest='undirected', action='store_false')
	parser.set_defaults(directed=False)

	return parser.parse_args()


def read_graph(args):
	'''
	Reads the input network in networkx.
	'''
	if args.weighted:
		G = nx.read_edgelist(args.input, nodetype=int, data=(('weight',float),), create_using=nx.DiGraph())
	else:
		G = nx.read_edgelist(args.input, nodetype=int, create_using=nx.DiGraph())
		for edge in G.edges():
			G[edge[0]][edge[1]]['weight'] = 1

	if not args.directed:
		G = G.to_undirected()

	return G


def learn_embeddings(walks):
	'''
	Learn embeddings by optimizing the Skipgram objective using SGD.
	'''
	walks = [list(map(str, walk)) for walk in walks]
	for i in walks:
		print(i)
	model = Word2Vec(walks, size=args.dimensions, window=args.window_size, min_count=0, sg=1, seed=1, workers=1, iter=args.iter)
	model.wv.save_word2vec_format(args.output)
	
	return


def main(args):
	'''
	Pipeline for representational learning for all nodes in a graph.
	'''
	nx_G = read_graph(args)
	G = node2vec.Graph(nx_G, args.directed, args.p, args.q)
	G.preprocess_transition_probs()
	walks = G.simulate_walks(args.num_walks, args.walk_length)
	learn_embeddings(walks)


if __name__ == "__main__":
	args = parse_args()
	args.input = 'user_edges'
	args.output = 'user_vec'
	args.walk_length = 5
	args.num_walks = 10
	# args.weighted = True
	# args.directed = True
	args.dimensions = 64
	args.window_size = 2
	args.p = 2
	args.q = 2
	main(args)
	model = KeyedVectors.load_word2vec_format('user_vec')
	print(model.wv.most_similar('4'))
