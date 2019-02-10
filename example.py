def test(x_train, y_train, x_test, y_test):
    model = LogisticRegression()
    model.train(x_train, y_train)
    # Evaluate using test data
    y_hat = model.predict(x_test, probs=True)
    return scipy.metrics.auc(y_test, y_hat)

def createSVR (x, y):
    svr = SVR()
    svr.train(x, y)
    return svr
    
def load_custom_model(path, x, y):
    if os.path.isfile(path):
        custom = pickle.load(path)
    else:
        custom = CustomClassifier()
        custom.train(x, y)
        # save
        pickle.dump(custom, path)
    return custom