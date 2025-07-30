from ._utils import ew_ret, vw_ret, remove_items, decimal, asterisk, qcut_with_exception
from ._renders import HtmlRenderer, DocxRenderer

import pandas as pd
import numpy as np
import statsmodels.api as sm

from IPython.display import display, HTML


def nw_ttest(df, ret, maxlags, model_cols=[]):
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

    if not maxlags:
        T = ols_model.nobs
        maxlags = int(4 * ((T / 100) ** (2 / 9)))

    reg_res = ols_model.fit(cov_type="HAC",
                            cov_kwds={'maxlags': maxlags}, kernel="bartlett")
    
    res_dict["mean"] = reg_res.params["const"]
    res_dict["tstats"] = reg_res.tvalues["const"]
    res_dict["pvalue"] = reg_res.pvalues["const"]
    
    return pd.Series(res_dict)

# sorting approach
class DoubleSorting(object):
    def __init__(self, data, sortbys, nqs, date, ret, mkt_cap):
        self.sortbys = sortbys
        self.nqs = nqs
        
        self.date = date
        self.ret = ret
        self.mkt_cap = mkt_cap
        
        columns = sortbys + [mkt_cap]
        self.data = data.dropna(subset=columns)
        self.data = self.data.reset_index(drop=True)
        
        self.data.index.name = "index"
        self.q_ret_name = "q_ret"
        
        
    def sorting(self, groupby, sortby, nq):
        # the smaller the label, the smaller the quantile
        labels = [i for i in range(1, nq+1)]
        
        groups = self.data.groupby(groupby, observed=False)
        quantiles = groups[sortby].apply(lambda x: qcut_with_exception(x, q=nq, labels=labels))
        
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
    
    
    def sequential(self, vw=False):
        sortby1, sortby2 = self.sortbys
        name1, name2 = sortby1 + "_q", sortby2  + "_q"
        nq1, nq2 = self.nqs
        
        groupby = [self.date]
        
        # sorting by variable 1
        self.data[name1] = self.sorting(groupby, sortby1, nq1)
        groupby.append(name1)
        # sorting by variable 2, sequentially
        self.data[name2] = self.sorting(groupby, sortby2, nq2)
        groupby.append(name2)
        
        # portfolio return for each sorting group
        quantile_ret = self.quantile_return(groupby, vw=vw)
        quantile_ret = quantile_ret.rename(columns={name1: sortby1, name2: sortby2})

        # wrap up results
        notes = [f"Sequential sorting: {sortby1} - {sortby2}"]
        results = SortingResults(quantile_ret, self.q_ret_name, 
                                 self.date, self.sortbys, notes)
        return results
    
    def independent(self, vw=False):
        sortby1, sortby2 = self.sortbys
        name1, name2 = sortby1 + "_q", sortby2 + "_q"
        nq1, nq2 = self.nqs
        
        groupby = [self.date]
        
        # sorting by variable 1
        self.data[name1] = self.sorting(groupby, sortby1, nq1)
        # sorting by variable 2, independently
        self.data[name2] = self.sorting(groupby, sortby2, nq2)
        
        groupby.append(name1)
        groupby.append(name2)
        
        # portfolio return for each sorting group
        quantile_ret = self.quantile_return(groupby, vw=vw)
        quantile_ret = quantile_ret.rename(columns={name1: sortby1, name2: sortby2})
        
        # wrap up results
        notes = [f"Independent sorting: {sortby1}, {sortby2}"]
        results = SortingResults(quantile_ret, self.q_ret_name, 
                                 self.date, self.sortbys, notes)
        return results

    
# results wrapper
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
        main = MainTable(self.res, self.qret, rf_df, rf, 
                         self.date, self.sortbys, layout=layout, raw_ret=raw_ret, **kwargs)
        
        if layout == "default":
            orientation = 'horizontal', "vertical"
        elif layout == "reverse":
            orientation = 'vertical', "horizontal"
            
        strategy1 = StrategyTable(qret_df=self.res, qret=self.qret, date=self.date,
                                  sortby_strategy=self.sortbys[0], sortby_other=self.sortbys[1],
                                  alpha_models=alpha_models,
                                  orientation=orientation[0], strategy=strategies[0],
                                  rf_df=rf_df, rf=rf, **kwargs)

        strategy2 = StrategyTable(qret_df=self.res, qret=self.qret, date=self.date,
                                  sortby_strategy=self.sortbys[1], sortby_other=self.sortbys[0],
                                  alpha_models=alpha_models,
                                  orientation=orientation[1], strategy=strategies[1],
                                  rf_df=rf_df, rf=rf,**kwargs)
        
        self.main = main
        self.strategies = [strategy1, strategy2]
        
        
    def _html_render(self, layout):
        main = self.main
        s1, s2 = self.strategies
        
        main_render = HtmlRenderer(main.means, main.tstats, main.hhead, 
                                   main.vhead, self.notes)
        main_html = main_render.render()
        
        render1 = HtmlRenderer(s1.means, s1.tstats, s1.hhead, 
                               s1.vhead, s1.notes)
        strategy1_html = render1.render()
        
        render2 = HtmlRenderer(s2.means, s2.tstats, s2.hhead, 
                               s2.vhead, s2.notes)
        strategy2_html = render2.render()
        
        if layout == "default":
            html1 = self.inline_render([main_html, strategy2_html])
            html2 = strategy1_html
        elif layout == "reverse":
            html1 = self.inline_render([main_html, strategy1_html])
            html2 = strategy2_html
            
        display(HTML(html1))
        display(HTML(html2))
        
        
    def _docx_save(self, output_path):
        main = self.main
        s1, s2 = self.strategies
        
        main_docx = DocxRenderer(main.means, main.tstats, main.hhead, main.vhead, self.notes)
        doc = main_docx.render()
        
        strategy1_docx = DocxRenderer(s1.means, s1.tstats, s1.hhead, 
                                      s1.vhead, s1.notes, doc=doc)
        doc = strategy1_docx.render()
        
        strategy2_docx = DocxRenderer(s2.means, s2.tstats, s2.hhead, 
                                      s2.vhead, s2.notes, doc=doc)
        doc = strategy2_docx.render()
        
        doc.save(output_path)
        print(f"\n\nFile saved at {output_path}")
        
        
    def summary(self, rf_df, rf, alpha_models, layout="default", 
                strategies=["HML", "HML"], raw_ret=False, output_path=None,
                **kwargs):
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
        raw_ret: show raw return in main table
                 rather than show excess return by default
        show_t: show tstats in main table
        show_stars: show asterisk in main table
        mean_decimal: decimal for means
        t_decimal: decimal for tstats
        nw_maxlags: max lags for Newey-West t stats
        '''
        
        self._make_table(rf_df, rf, alpha_models, layout, strategies, raw_ret, **kwargs)
        if raw_ret:
            self.notes.append("The above table reports raw return")
        else:
            self.notes.append("The above table reports excess return rather than raw return")
        self._html_render(layout)
        if output_path:
            self._docx_save(output_path)
            
    
# make tables
class MainTable(object):
    def __init__(self, qret_df, qret, rf_df, rf, date, sortbys, layout="default", raw_ret=False,
                 pct_sign=True, nw_maxlags=None, **kwargs):
        self.excess = "excess"

        if pct_sign:
            self.pct_sign = '%'
        else:
            self.pct_sign = ''
        
        qret_df = self.add_excess(qret_df, qret, rf_df, rf, date)
        if raw_ret:
            test_res = self.test_mean(qret_df=qret_df, excess=qret, sortbys=sortbys, maxlags=nw_maxlags, layout=layout)
        else:
            test_res = self.test_mean(qret_df=qret_df, excess=self.excess, sortbys=sortbys, maxlags=nw_maxlags, layout=layout)
        self.means = self.mean_table(test_res, **kwargs)
        self.tstats = self.tstats_table(test_res, **kwargs)
        
    
    def add_excess(self, qret_df, qret, rf_df, rf, date):
        qret_df = qret_df.merge(rf_df, on=date, how="left")
        qret_df[self.excess] = qret_df[qret] - qret_df[rf]
        
        return qret_df
    
    
    def test_mean(self, qret_df, excess, sortbys, maxlags, layout="default"):
        groups = qret_df.groupby(sortbys, observed=False)
        test_res = groups.apply(lambda x: nw_ttest(df=x, ret=excess, maxlags=maxlags, model_cols=[]))
        
        if layout == "default":
            test_res = test_res.unstack(-1)
            self.vhead, self.hhead = sortbys
        elif layout == "reverse":
            test_res = test_res.unstack(0)
            self.hhead, self.vhead = sortbys
        else:
            raise ValueError("Valid layout parameter: 'default' or 'reverse'")
            
        return test_res
    
    
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
    
    
class StrategyTable(object):
    def __init__(self, qret_df, qret, date, 
                 sortby_strategy, sortby_other, 
                 alpha_models,
                 orientation="vertical", strategy="HML",
                 pct_sign=True, **kwargs):
        
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
                                    sortby_strategy, sortby_other, 
                                    strategy)
        self.strategy_df = strategy_df
        
        alpha_models = [None] + alpha_models  # None for no model, i.e. excess return
        
        # iters models and caculate corresponding alphas
        self.get_alphas(date=date, strategy_df=strategy_df,
                        sortby_other=sortby_other,
                        alpha_models=alpha_models, **kwargs)
        # adjust according to orientation, add hhead and vhead
        self.orientation_adjust(orientation, sortby_strategy, sortby_other)
    
    def add_diff(self, qret_df, qret, date, sortby_strategy, sortby_other, strategy):
        qret_df = qret_df.set_index([date, sortby_other, sortby_strategy])
        qret_df = qret_df.unstack(sortby_strategy)[qret]
        
        columns = qret_df.columns
        hlabel, llabel = columns.max(), columns.min()
        
        if strategy == "HML":
            qret_df[self.excess] = qret_df[hlabel] - qret_df[llabel]
            self.notes.append(f"{sortby_strategy} strategy: high minus low")
        elif strategy == "LMH":
            qret_df[self.excess] = qret_df[llabel] - qret_df[hlabel]
            self.notes.append(f"{sortby_strategy} strategy: low minus high")
        else:
            raise ValueError("Valid strategy parameters: 'HML' or 'LMH'")
            
        # strategy_df = qret_df[self.excess].reset_index()
        # add strategy series on FC2 for previously added strategy series on FC1
        strategy_df = qret_df[self.excess].unstack(-1)
        strategy_df['H-L'] = strategy_df[5] - strategy_df[1]
        # format the strategy_df
        strategy_df = (strategy_df.stack()
                       .reset_index()
                       .rename(columns={0: self.excess})
                       )
        return strategy_df

    def test_mean(self, date, strategy_df, sortby_other,
                  maxlags, model=None):
        # if factor model data is omitted on term t
        # then term t would be dropped
        if isinstance(model, pd.DataFrame):
            model_cols = remove_items([date], model.columns)
            # add pricing model
            strategy_df = strategy_df.merge(model, on=date, how="left")
        else:
            model_cols = []
            # add excess return
            strategy_df = strategy_df.copy()
            
        groups = strategy_df.groupby(sortby_other, observed=False)
        test_res = groups.apply(lambda x: nw_ttest(df=x, ret=self.excess, maxlags=maxlags, model_cols=model_cols))
        
        return test_res, model_cols
    
    
    def mean_table(self, test_res, show_stars_strategy=True, 
                   mean_decimal=3, **kwargs):
        means = test_res["mean"].map(lambda x:
                                     decimal(x * 100, mean_decimal) + self.pct_sign)
        
        if show_stars_strategy:
            stars = test_res["pvalue"].map(asterisk)
            means += stars
            
        return means
    
    
    def tstats_table(self, test_res, show_t_strategy=True, 
                     t_decimal=3, **kwargs):
        if show_t_strategy:
            tstats = test_res["tstats"].map(lambda x:
                                            f"({decimal(x, t_decimal)})")
        else:
            tstats = test_res["tstats"].map(lambda x: "-")
            
        return tstats
    
    def get_alphas(self, date, strategy_df, sortby_other,
                   alpha_models, nw_maxlags=None, **kwargs):
        # wrap up functions: test_mean, mean_table and tstats_table
        # iters alpha models and calculate alpha
        means_ls = []
        tstats_ls = []
        for n, model in enumerate(alpha_models):
            test_res, model_cols = self.test_mean(date=date, strategy_df=strategy_df,
                                                  sortby_other=sortby_other, model=model,
                                                  maxlags=nw_maxlags)
            
            if n == 0:
                name = self.excess
            else:
                name = self.alpha_prefix + str(n)
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
        
    def orientation_adjust(self, orientation, sortby_strategy, sortby_other):
        if orientation == "vertical":
            self.hhead = f"{sortby_strategy} strategy"
            self.vhead = f"{sortby_other}"
        elif orientation == "horizontal":
            self.means = self.means.T
            self.tstats = self.tstats.T
            
            self.hhead = f"{sortby_other}"
            self.vhead = f"{sortby_strategy} strategy"