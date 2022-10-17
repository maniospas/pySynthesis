def laplacian_parameters(G, symm):
    # calculate asymmetric Laplacian normalization
    degv = {v : float(len(list(G.neighbors(v))))**symm for v in G.nodes()}
    degu = {u : float(len(list(G.neighbors(u))))**(1-symm) for u in G.nodes()}
    return degv, degu

def visualize(G, p):
    # normalize priors
    p_sum = sum(p.values())
    normalized_prior_ranks = {u: p[u]/p_sum for u in p}
    #
    print('----- Visualizing using d3 -----')
    data = {}
    data['nodes'] = [{'id':str(u),'color_intensity':normalized_prior_ranks[u]} for u in G.nodes()]
    data['links'] = [{'source':str(node1),'target':str(node2),'value':1} for node1,node2 in G.edges()]
    import os, json
    with open('visualize/data.json', 'w') as outfile:  
        json.dump(data, outfile)
    os.system('start firefox.exe "file:///'+os.getcwd()+'/visualize/visualize.html"')

def pagerank(G, prior_ranks, a, msq_error):
    # calculate normalization parameters of symmetric Laplacian
    degv = {v : float(len(list(G.neighbors(v))))**0.5 for v in G.nodes()}
    degu = {u : float(len(list(G.neighbors(u))))**0.5 for u in G.nodes()}
    # iterate to calculate PageRank
    ranks = prior_ranks
    while True:
        msq = 0
        next_ranks = {}
        for u in G.nodes():
            rank = sum(ranks[v]/degv[v]/degu[u] for v in G.neighbors(u))
            next_ranks[u] = rank*a + prior_ranks[u]*(1-a)
            msq += (next_ranks[u]-ranks[u])**2
        ranks = next_ranks
        if msq/len(G.nodes())<msq_error:
            break
    return ranks

def train_lr(x_train, y_train, preprocessing="normalize"):
    # create a logistic regression model
    model = LogisticRegression()
    # select preprocessing method
    if preprocessing == "normalize":
        # Normalize training data
        x_train = (x_train - x_train.min(axis=0)) / (x_train.max(axis=0) - x_train.min(axis=0))
    elif preprocessing == "standardize":
        # Standardize training data
        x_train = (x_train - x_train.mean(axis=0)) / (x_train.std(axis=0))
    # train
    model.train(x_train, y_train)
    return model


def test(x_train, y_train, x_test, y_test):
    # create a logistic regression
    model = LogisticRegression()
    model.train(x_train, y_train)
    # Evaluate using test data
    y_hat = model.predict(x_test, probs=True)
    return scipy.metrics.auc(y_test, y_hat)


def createSVR(x, y):
    # create an svr model
    svr = SVR()
    svr.train(x, y)
    return svr


def load_custom_model(path, CustomClassifier, x, y):
    if os.path.isfile(path):
        custom = pickle.load(path)
    else:
        custom = CustomClassifier()
        custom.train(x, y)
        # save
        pickle.dump(custom, path)
    return custom

