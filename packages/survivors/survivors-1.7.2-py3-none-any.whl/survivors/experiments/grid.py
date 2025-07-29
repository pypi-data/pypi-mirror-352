import numpy as np
import pandas as pd
import time
import os
import pickle

from sklearn.model_selection import StratifiedKFold, ParameterGrid, train_test_split
# from sklearn.preprocessing import StandardScaler

from .. import constants as cnt
from .. import metrics as metr
from ..external import LeafModel

try:
    import mgzip  # Custom
    from memory_profiler import memory_usage
    open_file = mgzip.open
    check_memory = lambda: memory_usage()[0]
except ImportError:
    open_file = open
    check_memory = lambda: np.nan


def to_str_from_dict_list(d, stratify):
    if isinstance(stratify, str):
        return str(d.get(stratify, ""))
    elif isinstance(stratify, list):
        return ";".join([str(d.get(e, "")) for e in stratify])
    return None


def stratify_by_time_cens(y):
    qs = np.quantile(y[cnt.TIME_NAME], np.linspace(0.2, 0.8, 4))
    time_discr = np.searchsorted(qs, y[cnt.TIME_NAME])
    discr = np.char.add(time_discr.astype(str), y[cnt.CENS_NAME].astype(str))
    return discr


def prepare_sample(X, y, train_index, test_index):
    """ Constructing a set of bins on target variables and clipping """
    X_train, X_test = X.iloc[train_index, :].copy(), X.iloc[test_index, :].copy()
    y_train, y_test = y[train_index], y[test_index]

    # too_late = np.quantile(y_train[cnt.TIME_NAME], 0.975)
    # ind_tr = np.where(y_train[cnt.TIME_NAME] > too_late)
    # y_train[cnt.CENS_NAME][ind_tr] = False
    # y_train[cnt.TIME_NAME][ind_tr] = too_late

    # ind_tst = np.where(y_test[cnt.TIME_NAME] > too_late)
    # y_test[cnt.CENS_NAME][ind_tst] = False
    # y_test[cnt.TIME_NAME][ind_tst] = too_late

    bins = cnt.get_bins(time=y_train[cnt.TIME_NAME], cens=y_train[cnt.CENS_NAME])
    # y_train[cnt.TIME_NAME] = np.clip(y_train[cnt.TIME_NAME], bins.min() - 1, bins.max() + 1)

    y_test[cnt.TIME_NAME] = np.clip(y_test[cnt.TIME_NAME], bins.min(), bins.max())
    return X_train, y_train, X_test, y_test, bins


def generate_sample(X, y, folds, mode="CV"):
    """
    Generate cross-validate samples with StratifiedKFold.

    Parameters
    ----------
    X : Pandas dataframe
        Contain input features of events.
    y : structured array
        Contain censuring flag and time of events.
    folds : int
        Quantity of cross-validate folds.
    mode : str
        Validation scenario.

    Yields
    ------
    X_train : Pandas dataframe
        Contain input features of train sample.
    y_train : array-like
        Contain censuring flag and time of train sample.
    X_test : Pandas dataframe
        Contain input features of test sample.
    y_test : array-like
        Contain censuring flag and time of test sample.
    bins : array-like
        Points of timeline.

    """

    discr = stratify_by_time_cens(y)
    if mode != "HOLD-OUT":
        skf = StratifiedKFold(n_splits=folds)

    if mode == "TIME-CV":
        train_index = np.array([], dtype=int)
        for train_index_, test_index_ in skf.split(X, discr):  # y[cnt.CENS_NAME]):
            if train_index.shape[0] > 0:
                X_train, y_train, X_test, y_test, bins = prepare_sample(X, y, train_index, test_index_)
                yield X_train, y_train, X_test, y_test, bins
            train_index = np.hstack([train_index, test_index_])
    elif mode == "CV+HOLD-OUT":
        X, y, X_HO, y_HO, bins_HO = next(generate_sample(X, y, folds=1, mode="HOLD-OUT"))
        for X_train, y_train, X_test, y_test, bins in generate_sample(X, y, folds=folds, mode="CV"):
            yield X_train, y_train, X_test, y_test, bins
        yield X, y, X_HO, y_HO, bins_HO
    elif mode == "HOLD-OUT":
        for i_fold in range(folds):
            X_TR, X_HO = train_test_split(X, stratify=discr,  # y[cnt.CENS_NAME],
                                          test_size=0.33, random_state=42 + i_fold)
            X_tr, y_tr, X_HO, y_HO, bins_HO = prepare_sample(X, y, X_TR.index, X_HO.index)
            yield X_tr, y_tr, X_HO, y_HO, bins_HO
    elif mode == "CV":
        for train_index, test_index in skf.split(X, discr):  # y[cnt.CENS_NAME]):
            X_train, y_train, X_test, y_test, bins = prepare_sample(X, y, train_index, test_index)
            yield X_train, y_train, X_test, y_test, bins
    pass


def count_metric(y_train, y_test, pred_time, pred_sf, pred_hf, bins, metrics_names):
    return np.array([metr.METRIC_DICT[metr_name](y_train, y_test, pred_time, pred_sf, pred_hf, bins)
                     for metr_name in metrics_names])


def get_name_file(method, params, mode, fold):
    """
    Creating a name to cache the model without considering variables independent for reproducibility.
    """
    filter_params = ["categ", "ens_metric_name", "aggreg_func", "n_jobs"]
    name_lst = [method.__name__]
    name_lst += [v for k, v in params.items() if not (k in filter_params)]
    name_lst += [mode, fold]
    return "_".join(map(str, name_lst))


def get_fit_eval_func(method, X, y, folds, metrics_names=['CI'], mode="CV", dir_path=None):
    """
    Return function, which on sample X, y apply cross-validation and calculate 
    metrics for each fold.

    Parameters
    ----------
    method : class
        Must have methods for fitting, predicting time, hazard and survival func
            
    X : Pandas dataframe
        Contain input features of events.
    y : structured array
        Contain censuring flag and time of events.
    folds : int
        Quantity of cross-validate folds.
    metrics_names : TYPE, optional
        DESCRIPTION. The default is ['CI'].
    mode : str
        Validation scenario.
    dir_path : str
        Path to cache directory (for loading pretrained models).

    Returns
    -------
    functions
        Recieve hyperparameters and return list of metrics arrays.
        Allow to use in ParameterGrid.

    """
    def f(**kwargs):
        metr_lst = []
        exec_times = []
        exec_mem = []
        fold = 0
        for X_train, y_train, X_test, y_test, bins in generate_sample(X, y, folds, mode):
            # print("X_train.shape:", X_train.shape)
            s_time = time.time()
            s_mem = [check_memory()]
            est = method(**kwargs)
            if method.__name__.find('CRAID') != -1:  # TODO replace to isinstance
                if dir_path is None:
                    est.fit(X_train, y_train)
                else:
                    name = os.path.join(dir_path, get_name_file(method, kwargs, mode, fold) + '.pkl')
                    if not os.path.exists(name):
                        print("Fitted from scratch")
                        est.fit(X_train, y_train)
                        with open_file(name, 'wb') as out:  # Custom
                            pickle.dump(est, out, pickle.HIGHEST_PROTOCOL)
                    with open_file(name, 'rb') as inp:
                        est = pickle.load(inp)

                est.aggreg_func = kwargs.get("aggreg_func", "mean")
                est.tolerance_find_best(kwargs.get("ens_metric_name", "IBS_REMAIN"))
                s_mem.append(check_memory())
                pred_sf = est.predict_at_times(X_test, bins=bins, mode="surv")
                pred_sf[:, -1] = 0
                pred_sf[:, 0] = 1
                pred_time = est.predict(X_test, target=cnt.TIME_NAME)
                pred_hf = est.predict_at_times(X_test, bins=bins, mode="hazard")
            elif isinstance(est, LeafModel):
                X_train.loc[:, cnt.TIME_NAME] = y_train[cnt.TIME_NAME]
                X_train.loc[:, cnt.CENS_NAME] = y_train[cnt.CENS_NAME]
                est.fit(X_train)
                pred_sf = est.predict_survival_at_times(X_test, bins=bins)
                pred_time = est.predict_feature(X_test, feature_name=cnt.TIME_NAME)
                pred_hf = est.predict_hazard_at_times(X_test, bins=bins)
            else:  # Methods from scikit-survival
                s = pd.isna(X_train).sum(axis=0) != X_train.shape[0]
                valid_feat = s[s].index
                med_val = 0
                # med_val = X_train[valid_feat].median()
                # med_val = X_train[valid_feat].mean()
                X_train = X_train[valid_feat].fillna(med_val).replace(np.nan, med_val).replace(np.inf, med_val)
                X_test = X_test[valid_feat].fillna(med_val).replace(np.nan, med_val).replace(np.inf, med_val)

                # scaler = StandardScaler()
                # X_train = scaler.fit_transform(X_train)
                # X_test = scaler.transform(X_test)

                est = est.fit(X_train, y_train)
                s_mem.append(check_memory())
                survs = est.predict_survival_function(X_test)
                hazards = est.predict_cumulative_hazard_function(X_test)
                pred_sf = np.array(list(map(lambda x: x(bins), survs)))
                pred_hf = np.array(list(map(lambda x: x(bins), hazards)))
                pred_time = -1 * est.predict(X_test)
                # pred_time = np.trapz(pred_sf, bins)
                # Integral version from: https://lifelines.readthedocs.io/en/latest/fitters/regression/CoxPHFitter.html

            exec_mem.append(max(s_mem) - min(s_mem))
            exec_times.append(time.time() - s_time)
            metr_lst.append(count_metric(y_train, y_test, pred_time,
                                         pred_sf, pred_hf, bins, metrics_names))
            fold += 1
            del est
        return np.vstack(metr_lst), np.array(exec_times), np.array(exec_mem)
    return f


def bins_scheme(val, scheme=""):
    if scheme == "rank":
        u = np.unique(val)
        ind = np.digitize(val, u)
        return (ind * val.max() / ind.max()).astype("int")
    if scheme == "quantile":
        u = np.unique(np.quantile(val, np.linspace(0, 1, 100)))
        ind = np.digitize(val, u)
        return (ind * val.max() / ind.max()).astype("int")
    if scheme == "log+scale":
        a = np.log(val+1)
        v = (val.max() - val.min())*(a - a.min())/(a.max() - a.min()) + val.min()
        return v.astype("int")
    return val


class Experiments(object):
    """
    Class receives methods, metrics and grids,
          produces cross-validation experiments,
          stores table of results : name, params, time, metrics (by sample and mean)

    Attributes
    ----------
    methods : list
        Must have predicting methods according to metrics:
            IBS - survival func
            IAUC - cumulative hazard func
            CI - occurred time
            CI_CENS - occurred time
    methods_grid : list
        Each grid is dictionary: key - param name, values - list
    metrics : list
        Each metric is string, which must be in METRIC_DICT
    is_table : boolean
        Flag of calculation ending
    folds : int
        Quantity of cross-validate folds.
    except_stop : bool
        Mode of ending because of exception.
        True - stop experiments with current method
        False - continue experiments
    dataset_name : str
        Unique name of current dataset (used for saving)

    Methods
    -------
    
    add_method : append method and its grid
    set_metrics : check and set list of metric name 
    run : start experiments with data X, y
    get_agg_results : choose for each method aggregated params by metric and aggreg
    save : export table as xlsx
    
    """
    def __init__(self, folds=5, except_stop=False, dataset_name="NONE_NAME", mode="CV", bins_sch=""):
        self.methods = []
        self.methods_grid = []
        self.metrics = ["CI"]
        self.metric_best_p = "IBS"
        self.way_best_p = "min"

        self.is_table = False
        self.folds = folds
        self.except_stop = except_stop
        self.dataset_name = dataset_name
        self.dir_path = None

        self.result_table = None
        self.sample_table = None
        self.mode = mode
        self.bins_sch = bins_sch

    def add_metric_best(self, metric):
        if metric in self.metrics:
            self.metric_best_p = metric
            self.way_best_p = "min" if metric in metr.DESCEND_METRICS else "max"

    def add_method(self, method, grid):
        self.methods.append(method)
        self.methods_grid.append(grid)
        
    def set_metrics(self, lst_metric):
        self.metrics = []
        for metr_name in lst_metric:
            if metr_name in metr.METRIC_DICT:
                self.metrics.append(metr_name)
            else:
                print(f"METRIC {metr_name} IS NOT DEFINED")
    
    def run(self, X, y, dir_path=None, verbose=0):
        self.dir_path = dir_path
        y["time"] = bins_scheme(y["time"], scheme=self.bins_sch)
        self.result_table = pd.DataFrame([], columns=["METHOD", "PARAMS", "TIME"] + self.metrics)

        for method, grid in zip(self.methods, self.methods_grid):
            fit_eval_func = get_fit_eval_func(method, X, y, self.folds, self.metrics, self.mode, self.dir_path)
            print(method, grid)

            grid_params = ParameterGrid(grid)
            p_size = len(grid_params)
            for i_p, p in enumerate(grid_params):
                try:
                    eval_metr, exec_times, exec_mem = fit_eval_func(**p)
                    curr_dict = {"METHOD": method.__name__, "CRIT": p.get("criterion", ""), "PARAMS": str(p),
                                 "TIMES": exec_times, "TIME": np.sum(exec_times),
                                 "MEMS": exec_mem, "MEM": np.sum(exec_mem)}
                    eval_metr = {m: eval_metr[:, i] for i, m in enumerate(self.metrics)}
                    curr_dict.update(eval_metr)
                    self.result_table = pd.concat([self.result_table, pd.DataFrame([curr_dict])], ignore_index=True)
                    if verbose > 0:
                        print(f"Iteration: {i_p + 1}/{p_size}")
                        print(f"EXECUTION TIME OF {method.__name__}: {exec_times.round(3)}, MEM {exec_mem.round(3)}",
                              {k: [round(np.mean(v), 3), round(v[-1], 3)] for k, v in eval_metr.items()})
                except KeyboardInterrupt:
                    print("Handled KeyboardInterrupt")
                    break
                except Exception as e:
                    print("Method: %s, Param: %s finished with except '%s'" % (method.__name__, str(p), e))
                    if self.except_stop:
                        break
                    curr_dict = {"METHOD": method.__name__, "CRIT": p.get("criterion", ""),
                                 "PARAMS": str(p), "TIME": -1}
                    curr_dict.update({m: np.array([np.nan, np.nan]) for i, m in enumerate(self.metrics)})
                    self.result_table = pd.concat([self.result_table, pd.DataFrame([curr_dict])], ignore_index=True)
        if self.mode in ["TIME-CV", "CV+HOLD-OUT"]:
            for m in self.metrics:
                self.result_table[f"{m}_pred_mean"] = self.result_table[m].apply(lambda x: np.mean(x[:-1]))
            for m in self.metrics:
                self.result_table[f"{m}_last"] = self.result_table[m].apply(lambda x: x[-1])

        for m in self.metrics:
            self.result_table[f"{m}_mean"] = self.result_table[m].apply(np.mean)

        self.is_table = True

    def run_effective(self, X, y, dir_path=None, verbose=0,
                      stratify_best=["criterion", "balance", "leaf_model", "l_reg"]):
        if not (self.mode in ["CV+SAMPLE"]):
            self.run(X, y, dir_path=dir_path, verbose=verbose)
            return None

        y["time"] = bins_scheme(y["time"], scheme=self.bins_sch)
        self.bins_sch = ""

        folds = 20 if self.mode == "CV+SAMPLE" else 1

        discr = stratify_by_time_cens(y)
        X_TR, X_HO = train_test_split(X, stratify=discr,  # y[cnt.CENS_NAME],
                                      test_size=0.33, random_state=42)
        X_tr, y_tr, X_HO, y_HO, bins_HO = prepare_sample(X, y, X_TR.index, X_HO.index)
        old_mode = self.mode
        self.mode = "CV"
        self.run(X_tr, y_tr, dir_path=dir_path, verbose=verbose)
        self.sample_table = self.eval_on_sample_by_best_params(X, y, folds=folds, stratify=stratify_best)
        self.mode = old_mode

    def eval_on_sample_by_best_params(self, X, y, folds=20, stratify="criterion"):
        best_table = self.get_best_by_mode(stratify=stratify)
        d = best_table.loc[:, ["METHOD", "PARAMS"]].to_dict(orient="tight")
        map_method_by_name = {m.__name__: m for m in self.methods}

        ho_exp = Experiments(folds=folds, dataset_name=self.dataset_name, mode="HOLD-OUT")
        ho_exp.set_metrics(self.metrics)
        for method_params in d["data"]:
            method = map_method_by_name[method_params[0]]
            params = eval(method_params[1])
            params = {k: [v] for k, v in params.items()}
            ho_exp.add_method(method, params)
        ho_exp.run(X, y, dir_path=self.dir_path, verbose=1)
        res_table = ho_exp.result_table.copy()
        for m in self.metrics:
            res_table[f"{m}_CV"] = best_table[m]
            res_table[f"{m}_CV_mean"] = best_table[f"{m}_mean"]
        return res_table

    @staticmethod
    def get_agg_results(result_table, by_metric, choose="median", stratify="criterion"):
        if not (by_metric in result_table.columns):
            return None
        df = result_table.copy()
        stratify_name = f"Stratify({stratify})"
        df[stratify_name] = df["PARAMS"].apply(lambda x: to_str_from_dict_list(eval(x), stratify))
        df["METHOD_FULL"] = df.apply(lambda x: x["METHOD"].replace("CRAID", f"Tree({x[stratify_name]})"), axis=1)

        best_table = pd.DataFrame([], columns=df.columns)
        for method in df['METHOD_FULL'].unique():
            sub_table = df[df["METHOD_FULL"] == method]
            if sub_table.shape[0] == 0:
                continue
            if choose == "max":
                best_ind = sub_table[by_metric].idxmax()
                if np.isnan(best_ind):
                    continue
                best_row = sub_table.loc[best_ind]
            elif choose == "min":
                best_ind = sub_table[by_metric].idxmin()
                if np.isnan(best_ind):
                    continue
                best_row = sub_table.loc[best_ind]
            else:
                best_row = sub_table.sort_values(by=by_metric).iloc[sub_table.shape[0] // 2]

            # best_table = best_table.append(dict(best_row), ignore_index=True)
            best_table = pd.concat([best_table, pd.DataFrame([dict(best_row)])], ignore_index=True)
        return best_table

    def get_cv_result(self, stratify="criterion"):
        df_cv_best = self.get_agg_results(self.result_table, self.metric_best_p + "_mean",
                                          choose=self.way_best_p, stratify=stratify)
        return df_cv_best

    def get_time_cv_result(self, stratify="criterion"):
        df_time_cv_best = self.get_agg_results(self.result_table, self.metric_best_p + "_pred_mean",
                                               choose=self.way_best_p, stratify=stratify)
        return df_time_cv_best

    def get_hold_out_result(self, stratify="criterion"):
        df_hold_out_best = self.get_agg_results(self.result_table, self.metric_best_p + "_pred_mean",
                                                choose=self.way_best_p, stratify=stratify)
        rename_d = {m + "_pred_mean": m + "_CV_mean" for m in self.metrics}
        rename_d.update({m + "_last": m + "_HO" for m in self.metrics})
        return df_hold_out_best.rename(rename_d, axis=1)

    def get_result(self):
        return self.result_table

    def get_sample_result(self):
        return self.sample_table

    def get_best_by_mode(self, stratify="criterion"):
        if self.mode == "CV":
            return self.get_cv_result(stratify=stratify)
        elif self.mode == "TIME-CV":
            return self.get_time_cv_result(stratify=stratify)
        elif self.mode in ["CV+HOLD-OUT"]:
            return self.get_hold_out_result(stratify=stratify)
        elif self.mode in ["CV+SAMPLE"]:
            return self.get_sample_result()
        return None

    def save(self, dir_path):
        self.result_table.to_excel(f"{dir_path + self.dataset_name}_FULL_TABLE.xlsx", index=False)
            
    # def plot_results(self, dir_path):
    #     df = self.result_table.copy()
    #     df['METHOD'] = df.apply(lambda x: x["METHOD"].replace("CRAID", "Tree(%s)" %(x['CRIT'])),
    #                                  axis = 1)
    #     for m in self.metrics:
    #         fig, axs = plt.subplots(1, figsize=(6, 9))
    #         plt.title("%s %s" % (self.dataset_name, m))
    #         plt.boxplot(df[m], labels = df['METHOD'])
    #         plt.xticks(rotation=90)
    #         plt.savefig(dir_path + self.dataset_name + "%s_boxplot.png" %(m))
    #         plt.close(fig)
