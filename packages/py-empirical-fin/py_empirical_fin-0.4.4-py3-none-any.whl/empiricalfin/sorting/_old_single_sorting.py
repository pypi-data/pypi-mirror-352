from ._utils import ew_ret, vw_ret, remove_items, decimal, asterisk
from ._renders import HtmlRenderer, DocxRenderer

import pandas as pd
import numpy as np
import statsmodels.api as sm

from IPython.display import display, HTML


def nw_ttest(df, ret, model_cols=[], maxlags=5):
    '''
    newey-west robust t test
    '''
    res_dict = {}

    dependent = df[ret]

    if model_cols:
        independent = sm.add_constant(df[model_cols])
    else:
        independent = pd.Series(np.ones_like(dependent),
                                index=dependent.index, name="const")

    ols_model = sm.OLS(dependent, independent, missing="drop")
    reg_res = ols_model.fit(cov_type="HAC",
                            cov_kwds={'maxlags': maxlags}, kernel="bartlett")

    res_dict["mean"] = reg_res.params["const"]
    res_dict["tstats"] = reg_res.tvalues["const"]
    res_dict["pvalue"] = reg_res.pvalues["const"]

    return pd.Series(res_dict)


class SingleSorting(object):
    def __init__(self, data, sortby, nq, date, ret, mkt_cap):
        self.sortbys = sortby
        self.nqs = nq

        self.date = date
        self.ret = ret
        self.mkt_cap = mkt_cap

        columns = [sortby] + [mkt_cap]
        self.data = data.dropna(subset=columns)
        self.data = self.data.reset_index(drop=True)

        self.data.index.name = "index"
        self.q_ret_name = "q_ret"

    def sorting(self, groupby, sortby, nq):
        # the smaller the label, the smaller the quantile
        labels = [i for i in range(1, nq + 1)]

        groups = self.data.groupby(groupby, observed=False)
        quantiles = groups[sortby].apply(lambda x: pd.qcut(x, q=nq, labels=labels))

        quantiles = quantiles.reset_index(level=-1)
        quantiles = quantiles.reset_index(drop=True).set_index("index")
        return quantiles

    def quantile_return(self, groupby, vw):
        if vw:
            ret_func = vw_ret
        else:
            ret_func = ew_ret

        groups = self.data.groupby(groupby, observed=False)
        quantile_ret = groups.apply(lambda x: ret_func(data=x,
                                                       ret_col=self.ret,
                                                       mkt_cap_col=self.mkt_cap))
        quantile_ret.name = self.q_ret_name
        quantile_ret = quantile_ret.reset_index()
        return quantile_ret

    def single(self, vw=False):
        sortby1 = self.sortbys
        name1 = sortby1 + "_q"
        nq1 = self.nqs

        groupby = [self.date]

        # sorting by variable 1
        self.data[name1] = self.sorting(groupby, sortby1, nq1)
        groupby.append(name1)

        # portfolio return for each sorting group
        quantile_ret = self.quantile_return(groupby, vw=vw)
        quantile_ret = quantile_ret.rename(columns={name1: sortby1})

        # wrap up results
        notes = [f"Single sorting: {sortby1}"]
        results = SortingResults(quantile_ret, self.q_ret_name,
                                 self.date, self.sortbys, notes)
        return results


class SortingResults(object):
    def __init__(self, quantile_ret, qret, date, sortbys, init_notes=[]):
        self.res = quantile_ret
        self.notes = init_notes
        self.sortbys = sortbys
        self.qret, self.date = qret, date

    def inline_render(self, htmls):
        container = '<div style="display:flex;">'
        for n, html in enumerate(htmls):
            container += '<div style="margin-right: 20px;">'
            container += html
            container += '</div>'
        container += '</div>'
        return container

    def _make_table(self, rf_df, rf, alpha_models, layout, strategies, raw_ret, **kwargs):
        main = MainTable(qret_df=self.res, qret=self.qret, rf_df=rf_df, rf=rf,
                         date=self.date, sortbys=self.sortbys, alpha_models=alpha_models,
                         layout=layout, raw_ret=raw_ret, **kwargs)

        strategy1 = StrategyTable(qret_df=self.res, qret=self.qret, date=self.date,
                                  sortby=self.sortbys, alpha_models=alpha_models,
                                  layout=layout, strategy=strategies,
                                  rf_df=rf_df, rf=rf, **kwargs)

        self.main = main
        self.strategies = strategy1

    def _html_render(self):
        main = self.main
        s1 = self.strategies

        main_render = HtmlRenderer(main.means, main.tstats, main.hhead,
                                   main.vhead, self.notes+main.notes)
        main_html = main_render.render()

        render1 = HtmlRenderer(s1.means, s1.tstats, s1.hhead,
                               s1.vhead, s1.notes)
        strategy1_html = render1.render()

        html1 = self.inline_render([main_html, strategy1_html])

        display(HTML(html1))

    def _docx_save(self, output_path):
        main = self.main
        s1 = self.strategies

        main_docx = DocxRenderer(main.means, main.tstats, main.hhead, main.vhead,
                                 self.notes+main.notes)
        doc = main_docx.render()

        strategy1_docx = DocxRenderer(s1.means, s1.tstats, s1.hhead,
                                      s1.vhead, s1.notes, doc=doc)
        doc = strategy1_docx.render()

        doc.save(output_path)
        print(f"\n\nFile saved at {output_path}")

    def summary(self, rf_df, rf, alpha_models, layout="default",
                strategies="HML", raw_ret=False, output_path=None, **kwargs):
        '''
        Show excess return in main table by default

        -- rf_df:
        a dataframe of risk-free rate and corresponding date
        date column should be consistent with the data in sorting approach

        -- rf: column of risk-free rate in rf_df

        -- alpha_models:
        a sequence of dataframes, each represents a pricing model used to calculate alpha
        date column should be consistent with the data in sorting approach

        -- strategies:
        a sequence of 'HML' or 'LMH', strategy for each sorting variable
        'HML' represents hign minus low, 'LMH' represents low minus high

        --raw_ret:
        set raw_ret=True to show raw return in main table
        rather than show excess return by default

        -- output_path:
        output results to a Microsoft Word file

        -- kwargs
        show_t: show tstats in main table
        show_stars: show asterisk in main table
        mean_decimal: decimal for means
        t_decimal: decimal for tstats
        '''
        self._make_table(rf_df, rf, alpha_models, layout, strategies, raw_ret, **kwargs)
        self._html_render()
        if output_path:
            self._docx_save(output_path)


# make tables
class MainTable(object):
    def __init__(self, qret_df, qret, rf_df, rf, date, sortbys, alpha_models,
                 layout="default", raw_ret=False, pct_sign=True, **kwargs):
        # init params
        self.alpha_prefix = "alpha "
        self.excess = 'excess'
        self.raw = 'raw return'
        self.maxlags = 5
        self.notes = []

        if pct_sign:
            self.pct_sign = '%'
        else:
            self.pct_sign = ''

        if raw_ret:
            self.col1 = self.raw
            self.notes.append("The first column reports raw return")
        else:
            self.col1 = self.excess
            self.notes.append("The first column reports excess return")

        # raw return
        qret_df[self.raw] = qret_df[qret]
        # add excess return
        qret_df = self.add_excess(qret_df, qret, rf_df, rf, date)

        alpha_models = [None] + alpha_models  # None for no model, i.e. excess return
        # iters models and caculate corresponding alphas
        self.get_alphas(date=date, qret_df=qret_df, sortbys=sortbys,
                        alpha_models=alpha_models, **kwargs)
        # adjust according to orientation, add hhead and vhead
        self.orientation_adjust(layout, sortbys)


    def add_excess(self, qret_df, qret, rf_df, rf, date):
        qret_df = qret_df.merge(rf_df, on=date, how="left")
        qret_df[self.excess] = qret_df[qret] - qret_df[rf]

        return qret_df


    def test_mean(self, date, qret_df, excess, sortbys, model=None):
        # add model data to the qret_df
        if isinstance(model, pd.DataFrame):
            model_cols = remove_items([date], model.columns)
            qret_df = qret_df.merge(model, on=date, how="left")
        else:
            model_cols = []
            qret_df = qret_df.copy()

        # for each sort group, perform t-test
        groups = qret_df.groupby(sortbys, observed=False)
        test_res = groups.apply(lambda x: nw_ttest(x, excess, model_cols, maxlags=self.maxlags))
        test_res = test_res.unstack()

        return test_res, model_cols

    def mean_table(self, test_res, show_stars=False, mean_decimal=3, **kwargs):
        means = test_res["mean"].map(lambda x:
                                     decimal(x * 100, mean_decimal) + self.pct_sign)

        if show_stars:
            stars = test_res["pvalue"].map(asterisk)
            means += stars

        return means


    def tstats_table(self, test_res, show_t=False, t_decimal=3, **kwargs):
        if show_t:
            tstats = test_res["tstats"].map(lambda x:
                                            f"({decimal(x, t_decimal)})")
        else:
            tstats = test_res["tstats"].map(lambda x: "-")

        return tstats


    def get_alphas(self, date, qret_df, sortbys, alpha_models, **kwargs):
        # wrap up functions: test_mean, mean_table and tstats_table
        # iters alpha models and calculate alpha
        means_ls = []
        tstats_ls = []

        for n, model in enumerate(alpha_models):
            if n == 0:
                name = self.col1
                test_res, model_cols = self.test_mean(date=date, qret_df=qret_df, excess=self.col1,
                                                      sortbys=sortbys, model=model)
            else:
                name = self.alpha_prefix + str(n)
                test_res, model_cols = self.test_mean(date=date, qret_df=qret_df, excess=self.excess,
                                                      sortbys=sortbys, model=model)
                # add note to show variables in the model
                self.notes.append(name + f" model: {' ,'.join(model_cols)}")

            means = self.mean_table(test_res, **kwargs)
            tstats = self.tstats_table(test_res, **kwargs)

            means.name = name
            tstats.name = name
            means_ls.append(means)
            tstats_ls.append(tstats)

        self.means = pd.concat(means_ls, axis=1)
        self.tstats = pd.concat(tstats_ls, axis=1)


    def orientation_adjust(self, layout, sortbys):
        if layout == "default":
            self.hhead = "Return"
            self.vhead = sortbys

        elif layout == "reverse":
            self.means = self.means.T
            self.tstats = self.tstats.T

            self.hhead = sortbys
            self.vhead = "Return"
        else:
            raise ValueError("Valid layout parameter: 'default' or 'reverse'")


class StrategyTable(object):
    def __init__(self, qret_df, qret, date,
                 sortby, alpha_models,
                 layout, strategy="HML", pct_sign=True, **kwargs):

        self.alpha_prefix = "alpha "
        self.excess = "excess"
        self.maxlags = 5
        self.notes = []

        if pct_sign:
            self.pct_sign = '%'
        else:
            self.pct_sign = ''

        # calculate the difference of return between high and low portfolios
        strategy_df = self.add_diff(qret_df, qret, date,
                                    sortby, strategy)

        alpha_models = [None] + alpha_models  # None for no model, i.e. excess return

        # iters models and caculate corresponding alphas
        self.get_alphas(date=date, strategy_df=strategy_df,
                        alpha_models=alpha_models, **kwargs)
        # adjust according to orientation, add hhead and vhead
        self.orientation_adjust(layout, sortby)

    def add_diff(self, qret_df, qret, date, sortby, strategy):
        qret_df = qret_df.set_index([date, sortby])
        qret_df = qret_df.unstack().loc[:, qret]

        columns = qret_df.columns
        hlabel, llabel = columns.max(), columns.min()
        # hlabel: high value group label, llabel: low value group label
        self.hlabel, self.llabel = hlabel, llabel

        if strategy == "HML":
            qret_df[self.excess] = qret_df[hlabel] - qret_df[llabel]
            self.notes.append(f"{sortby} strategy: high minus low")
        elif strategy == "LMH":
            qret_df[self.excess] = qret_df[llabel] - qret_df[hlabel]
            self.notes.append(f"{sortby} strategy: low minus high")
        else:
            raise ValueError("Valid strategy parameters: 'HML' or 'LMH'")

        strategy_df = qret_df[self.excess].reset_index()
        return strategy_df

    def test_mean(self, date, strategy_df,
                  model=None):
        if isinstance(model, pd.DataFrame):
            model_cols = remove_items([date], model.columns)
            # add pricing model
            strategy_df = strategy_df.merge(model, on=date, how="left")
        else:
            model_cols = []
            strategy_df = strategy_df.copy()

        test_res = nw_ttest(strategy_df, self.excess, model_cols, maxlags=self.maxlags)

        return test_res, model_cols

    def mean_table(self, test_res, show_stars_strategy=True,
                   mean_decimal=3, **kwargs):
        means = decimal(test_res["mean"] * 100, mean_decimal) + self.pct_sign

        if show_stars_strategy:
            stars = asterisk(test_res["pvalue"])
            means += stars

        return means

    def tstats_table(self, test_res, show_t_strategy=True,
                     t_decimal=3, **kwargs):
        if show_t_strategy:
            tstats = "({})".format(decimal(test_res["tstats"], t_decimal))

        else:
            tstats = "-"

        return tstats

    def get_alphas(self, date, strategy_df,
                   alpha_models, **kwargs):
        # wrap up functions: test_mean, mean_table and tstats_table
        # iters alpha models and calculate alpha
        means_dict = {}
        tstats_dict = {}
        for n, model in enumerate(alpha_models):
            test_res, model_cols = self.test_mean(date=date, strategy_df=strategy_df,
                                                  model=model)

            if n == 0:
                name = self.excess
            else:
                name = self.alpha_prefix + str(n)
                # add note to show variables in the model
                self.notes.append(name + f" model: {' ,'.join(model_cols)}")

            means = self.mean_table(test_res, **kwargs)
            tstats = self.tstats_table(test_res, **kwargs)

            means_dict[name] = means
            tstats_dict[name] = tstats

        self.means = pd.DataFrame(pd.Series(means_dict)).rename(columns={0: " "})
        self.tstats = pd.DataFrame(pd.Series(tstats_dict)).rename(columns={0: " "})

    def orientation_adjust(self, layout, sortby):
        if layout == "reverse":
            self.hhead = "Return"
            self.vhead = f"{sortby} strategy"

        elif layout == "default":
            self.means = self.means.T
            self.tstats = self.tstats.T

            self.hhead = f"{sortby} strategy"
            self.vhead = "Return"
