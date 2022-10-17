import pygrank as pg


def test_pagerank(alpha=0.9):
    # load a small graph
    graph = pg.load_data(["graph9"])
    # define the pagerank algorithm
    algorithm = pg.PageRank(alpha)
    # run the algorithm
    return algorithm.rank(graph)


def algorithm_comparison():
    # load a bipartite graph
    loaded = pg.load_dataset_one_community(["bigraph"])
    graph = loaded[0]
    group = loaded[1]
    # convert group to graph signal
    signal = pg.to_signal(graph, group)
    # split signal to training and test subsets
    split = pg.split(signal, fraction_of_training=0.5)
    train = split[0]
    test = split[1]
    # create default pagerank
    ppr = pg.PageRank()
    # create default heat kernel
    hk = pg.HeatKernel()
    # define AUC as the measure of choice
    measure = pg.AUC(test, train)
    # assess
    print(measure(ppr.rank(train)))
    # assess
    print(measure(hk.rank(train)))


def test_personalized_heatkernel(k=3):
    # load a bipartite graph
    loaded = pg.load_dataset_one_community(["bigraph"])
    graph = loaded[0]
    group = loaded[1]
    # convert group to graph signal
    signal = pg.to_signal(graph, group)
    # define the heat kernel algorithm
    algorithm = pg.HeatKernel(k)
    # run the personalized version of the algorithm
    return algorithm.rank(signal)


