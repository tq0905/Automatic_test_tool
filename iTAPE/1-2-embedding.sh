# following step requires the source codes of OpenNMT. this step will generate initial embedding weights based on glove vectors.
OpenNMT-py/tools/embeddings_to_torch.py -emb_file_both "data/glove.6B.100d.txt" -dict_file "data/data.vocab.pt" -output_file "data/embeddings"
exec /bin/bash