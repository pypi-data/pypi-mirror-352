from ._utils import ew_ret, vw_ret, remove_items, decimal, asterisk
from ._renders import HtmlRenderer, DocxRenderer

import pandas as pd
import numpy as np
import statsmodels.api as sm

from IPython.display import display, HTML

def region_nw_ttest(df, ret, regionby, model_cols=[], maxlags=5):
    res_dict = {}

    dependent = df[ret]

    dummies = pd.get_dummies(df[regionby]).astype(int)
    dummy_cols = dummies.columns.to_list()
    df = pd.concat([df, dummies], axis=1)

    if model_cols:
        independent = df[dummy_cols + model_cols]
    else:
        independent = df[dummy_cols]

    ols_model = sm.OLS(dependent, independent, missing="drop")
    reg_res = ols_model.fit(cov_type="HAC",
                            cov_kwds={'maxlags': maxlags}, kernel="bartlett")

    for col in dummy_cols:
        res_dict[col] = pd.Series({'mean': reg_res.params[col],
                                   'tstats': reg_res.tvalues[col],
                                   'pvalue': reg_res.pvalues[col]})

    return pd.DataFrame(res_dict)


def region_diff_nw_ttest(df, ret,
                         regionby, minuend, substrahend,
                         model_cols=[], maxlags=5):

    dependent = df[ret]

    dummies = pd.get_dummies(df[regionby]).astype(int)
    dummies[substrahend] = dummies[substrahend] + dummies[minuend]
    dummy_cols = dummies.columns.to_list()
    df = pd.concat([df, dummies], axis=1)

    if model_cols:
        independent = df[dummy_cols + model_cols]
    else:
        independent = df[dummy_cols]

    ols_model = sm.OLS(dependent, independent, missing="drop")
    reg_res = ols_model.fit(cov_type="HAC",
                            cov_kwds={'maxlags': maxlags}, kernel="bartlett")

    return pd.Series({'mean': reg_res.params[minuend],
                      'tstats': reg_res.tvalues[minuend],
                      'pvalue': reg_res.pvalues[minuend]})


# sorting approach
class RegionSorting(object):
    def __init__(self, data, region_data, sortby, nq, nregion, date, ret, mkt_cap):
        self.sortby = sortby
        self.nq = nq

        self.regionby = remove_items([date], region_data.columns)[0]
        self.nregion = nregion
        
        self.date = date
        self.ret = ret
        self.mkt_cap = mkt_cap
        
        columns = [sortby, mkt_cap]
        self.data = data.dropna(subset=columns)
        self.data = self.data.reset_index(drop=True)
        
        self.data.index.name = "index"
        self.q_ret_name = "q_ret"

        self.region_data = region_data
        
        
    def sorting(self, groupby, sortby, nq):
        # the smaller the label, the smaller the quantile
        labels = [i for i in range(1, nq+1)]
        
        groups = self.data.groupby(groupby, observed=False)
        quantiles = groups[sortby].apply(lambda x: pd.qcut(x, q=nq, labels=labels))
        
        quantiles = quantiles.reset_index(level=-1)
        quantiles = quantiles.reset_index(drop=True).set_index("index")
        return quantiles


    def region_sorting(self):
        region_quantiles = self.region_data.copy()

        # the smaller the label, the smaller the quantile
        labels = [i for i in range(1, self.nregion + 1)]

        region_quantiles[self.regionby] = pd.qcut(self.region_data[self.regionby],
                                                  q=self.nregion, labels=labels)

        return region_quantiles


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
        sortby = self.sortby
        name = sortby + "_q"
        nq = self.nq

        groupby = [self.date]

        # sorting by variable 1
        self.data[name] = self.sorting(groupby, sortby, nq)
        groupby.append(name)

        # portfolio return for each sorting group
        quantile_ret = self.quantile_return(groupby, vw=vw)
        quantile_ret = quantile_ret.rename(columns={name: sortby})

        return quantile_ret


    def region(self, vw=False):
        qret_df = self.single(vw=vw)
        # only keep dates that show in single sorting
        unique_dates = qret_df[self.date].unique()
        self.region_data = self.region_data.query(f"{self.date}.isin(@unique_dates)")

        qregion_df = self.region_sorting()

        # records with missing region data will be dropped
        region_quantile_ret = qret_df.merge(qregion_df, on=self.date, how='left')
        region_quantile_ret = region_quantile_ret.dropna(subset=[self.regionby])

        # wrap up results
        notes = [f"Single sorting: {self.sortby}, Region sorting: {self.regionby}"]
        results = SortingResults(quantile_ret=region_quantile_ret, qret=self.q_ret_name,
                                 date=self.date, sortby=self.sortby, regionby=self.regionby,
                                 init_notes=notes)

        return results

    
# results wrapper
class SortingResults(object):
    def __init__(self, quantile_ret, qret, date, sortby, regionby, init_notes=[]):
        self.res = quantile_ret
        self.notes = init_notes
        self.sortby, self.regionby = sortby, regionby
        self.qret, self.date = qret, date
        
        
    def inline_render(self, htmls):
        container = '<div style="display:flex;">'
        for n, html in enumerate(htmls):
            container += '<div style="margin-right: 20px;">'
            container += html
            container += '</div>'
        container += '</div>'
        return container


    def _make_table(self, rf_df, rf, alpha_models, layout,
                    sort_strategy, region_strategy,
                    raw_ret, maxlags, **kwargs):
        main = MainTable(qret_df=self.res, qret=self.qret, rf_df=rf_df, rf=rf,
                         date=self.date, sortby=self.sortby, regionby=self.regionby,
                         layout=layout, raw_ret=raw_ret, maxlags=maxlags, **kwargs)
        
        if layout == "default":
            orientation = 'horizontal', "vertical"
        elif layout == "reverse":
            orientation = 'vertical', "horizontal"

        sort_strategy_table = SortStrategyTable(qret_df=self.res, qret=self.qret, date=self.date,
                                          sortby=self.sortby, regionby=self.regionby,
                                          alpha_models=alpha_models,
                                          orientation=orientation[0],
                                          sort_strategy=sort_strategy, region_strategy=region_strategy,
                                          rf_df=rf_df, rf=rf, maxlags=maxlags, **kwargs)

        region_strategy_table = RegionStrategyTable(qret_df=self.res, qret=self.qret, date=self.date,
                                              sortby=self.sortby, regionby=self.regionby,
                                              alpha_models=alpha_models,
                                              orientation=orientation[1],
                                              sort_strategy=sort_strategy, region_strategy=region_strategy,
                                              rf_df=rf_df, rf=rf, maxlags=maxlags, **kwargs)
        
        self.main = main
        self.strategies = [sort_strategy_table, region_strategy_table]
        
        
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
                sort_strategy="HML", region_strategy="HML",
                raw_ret=False, output_path=None, maxlags=5,
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
        '''

        self._make_table(rf_df=rf_df, rf=rf, alpha_models=alpha_models, layout=layout,
                         sort_strategy=sort_strategy, region_strategy=region_strategy,
                         raw_ret=raw_ret, maxlags=maxlags, **kwargs)
        if raw_ret:
            self.notes.append("The above table reports raw return")
        else:
            self.notes.append("The above table reports excess return rather than raw return")
        self._html_render(layout)
        if output_path:
            self._docx_save(output_path)
            
    
# make tables
class MainTable(object):
    def __init__(self, qret_df, qret, rf_df, rf, date, sortby, regionby,
                 layout="default", raw_ret=False,
                 pct_sign=True, maxlags=5, **kwargs):
        self.excess = "excess"
        self.maxlags = maxlags

        if pct_sign:
            self.pct_sign = '%'
        else:
            self.pct_sign = ''
        
        qret_df = self.add_excess(qret_df, qret, rf_df, rf, date)
        if raw_ret:
            test_res = self.test_mean(qret_df=qret_df, excess=qret, sortby=sortby, regionby=regionby,
                                      layout=layout)
        else:
            test_res = self.test_mean(qret_df=qret_df, excess=self.excess, sortby=sortby, regionby=regionby,
                                      layout=layout)
        self.means = self.mean_table(test_res, **kwargs)
        self.tstats = self.tstats_table(test_res, **kwargs)
        
    
    def add_excess(self, qret_df, qret, rf_df, rf, date):
        qret_df = qret_df.merge(rf_df, on=date, how="left")
        qret_df[self.excess] = qret_df[qret] - qret_df[rf]
        
        return qret_df
    
    
    def test_mean(self, qret_df, excess, sortby, regionby, layout="default"):
        groups = qret_df.groupby(sortby, observed=False)
        # groupby sorting varaible and test each sorting group on each region by adding region dummy in regression
        test_res = groups.apply(lambda x: region_nw_ttest(df=x, ret=excess, regionby=regionby,
                                                          model_cols=[], maxlags=self.maxlags))
        test_res = test_res.stack().unstack(1)
        
        if layout == "default":
            test_res = test_res.unstack(-1)
            self.vhead, self.hhead = sortby, regionby
        elif layout == "reverse":
            test_res = test_res.unstack(0)
            self.hhead, self.vhead = sortby, regionby
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
    

class SortStrategyTable(object):
    def __init__(self, qret_df, qret, date,
                 sortby, regionby,
                 alpha_models,
                 rf_df, rf,
                 orientation="vertical",
                 sort_strategy="HML", region_strategy="HML",
                 pct_sign=True, maxlags=5, **kwargs):

        self.alpha_prefix = "alpha "

        self.date=date

        self.excess = "excess"

        self.maxlags = maxlags
        self.notes = []

        if pct_sign:
            self.pct_sign = '%'
        else:
            self.pct_sign = ''

        # calculate the difference of return between high and low portfolios
        # only keep a column of difference of return
        strategy_df = self.add_diff(qret_df, qret, date,
                                    sortby, regionby,
                                    sort_strategy)
        self.strategy_df = strategy_df

        alpha_models = [None] + alpha_models  # None for no model, i.e. excess return

        # iters models and call test_mean function to caculate corresponding alphas for each region
        # store table results in self.means and self.tstats
        self.get_alphas_by_region(date=date, strategy_df=strategy_df,
                                  regionby=regionby,
                                  alpha_models=alpha_models, **kwargs)

        self.get_alphas_region_diff(date=date, strategy_df=strategy_df,
                                    regionby=regionby, region_strategy=region_strategy,
                                    alpha_models=alpha_models)

        # adjust according to orientation, add hhead and vhead
        self.orientation_adjust(orientation, sortby, regionby)


    def add_diff(self, qret_df, qret, date, sortby, regionby, strategy):
        qret_df = qret_df.set_index([date, regionby, sortby])
        qret_df = qret_df.unstack(sortby)[qret]

        columns = qret_df.columns
        hlabel, llabel = columns.max(), columns.min()

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

    def test_mean(self, date, strategy_df, regionby,
                  model=None):
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

        test_res = region_nw_ttest(df=strategy_df, ret=self.excess, regionby=regionby,
                                   model_cols=model_cols, maxlags=self.maxlags)
        test_res = test_res.T
        # groups = strategy_df.groupby(regionby, observed=False)
        # test_res = groups.apply(lambda x: nw_ttest(x, self.excess, model_cols, maxlags=self.maxlags))

        return test_res, model_cols


    def test_region_diff(self, date, strategy_df,
                         regionby, minuend, substrahend,
                         model=None):
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

        test_res = region_diff_nw_ttest(df=strategy_df, ret=self.excess,
                                        regionby=regionby, minuend=minuend, substrahend=substrahend,
                                        model_cols=model_cols, maxlags=self.maxlags)

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


    def get_alphas_by_region(self, date, strategy_df, regionby,
                             alpha_models, **kwargs):
        # wrap up functions: test_mean, mean_table and tstats_table
        # iters alpha models and calculate alpha
        means_ls = []
        tstats_ls = []
        for n, model in enumerate(alpha_models):
            test_res, model_cols = self.test_mean(date=date, strategy_df=strategy_df,
                                                  regionby=regionby, model=model)

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


    def get_alphas_region_diff(self, date, strategy_df,
                               regionby, region_strategy,
                               alpha_models, **kwargs):

        labels = strategy_df[regionby].unique()
        hlabel, llabel = labels.max(), labels.min()

        if region_strategy == "HML":
            minuend, substrahend = hlabel, llabel
            group_name = 'H-L'
        elif region_strategy == "LMH":
            minuend, substrahend = llabel, hlabel
            group_name = 'L-H'
        else:
            raise ValueError("Valid strategy parameters: 'HML' or 'LMH'")

        means_ls = []
        tstats_ls = []
        for n, model in enumerate(alpha_models):
            test_res, model_cols = self.test_region_diff(date=date, strategy_df=strategy_df,
                                                         regionby=regionby, minuend=minuend, substrahend=substrahend,
                                                         model=model)

            test_res = pd.DataFrame(test_res).T.rename(index={0: group_name})

            if n == 0:
                name = self.excess
            else:
                name = self.alpha_prefix + str(n)

            means = self.mean_table(test_res, **kwargs)
            tstats = self.tstats_table(test_res, **kwargs)
            means.name = name
            tstats.name = name

            means_ls.append(means)
            tstats_ls.append(tstats)

        means = pd.concat(means_ls, axis=1)
        tstats = pd.concat(tstats_ls, axis=1)
        self.means = pd.concat([self.means, means])
        self.tstats = pd.concat([self.tstats, tstats])


    def orientation_adjust(self, orientation, sortby, regionby):
        if orientation == "vertical":
            self.hhead = f"{sortby} strategy"
            self.vhead = f"{regionby}"
        elif orientation == "horizontal":
            self.means = self.means.T
            self.tstats = self.tstats.T

            self.hhead = f"{regionby}"
            self.vhead = f"{sortby} strategy"


class RegionStrategyTable(object):
    def __init__(self, qret_df, qret, date,
                 sortby, regionby,
                 alpha_models,
                 rf_df, rf,
                 orientation="vertical",
                 sort_strategy="HML", region_strategy="HML",
                 pct_sign=True, maxlags=5, **kwargs):

        self.alpha_prefix = "alpha "

        self.date=date

        self.rf_df = rf_df
        self.rf = rf

        self.excess = "excess"

        self.maxlags = maxlags
        self.notes = []

        if pct_sign:
            self.pct_sign = '%'
        else:
            self.pct_sign = ''

        # calculate the difference of return between high and low portfolios
        strategy_df = self.add_diff(qret_df=qret_df, qret=qret, date=date,
                                    sortby=sortby, regionby=regionby,
                                    sort_strategy=sort_strategy)
        self.strategy_df = strategy_df

        alpha_models = [None] + alpha_models  # None for no model, i.e. excess return

        # iters models and caculate corresponding alphas
        self.get_alphas_region_diff(date=date, strategy_df=strategy_df,
                                    sortby=sortby, regionby=regionby, region_strategy=region_strategy,
                                    alpha_models=alpha_models, **kwargs)

        # adjust according to orientation, add hhead and vhead
        self.orientation_adjust(orientation, sortby, regionby)


    def add_excess(self, qret_df, qret, rf_df, rf, date):
        qret_df = qret_df.merge(rf_df, on=date, how="left")
        qret_df[self.excess] = qret_df[qret] - qret_df[rf]

        return qret_df


    def add_diff(self, qret_df, qret, date, sortby, regionby, sort_strategy):
        # add excess return
        qret_df = self.add_excess(qret_df=qret_df, qret=qret,
                                  rf_df=self.rf_df, rf=self.rf, date=self.date)
        qret_df = qret_df.set_index([date, regionby, sortby])[self.excess]
        qret_df = qret_df.unstack(sortby)

        columns = qret_df.columns
        hlabel, llabel = columns.max(), columns.min()

        if sort_strategy == "HML":
            qret_df['H-L'] = qret_df[hlabel] - qret_df[llabel]
        elif sort_strategy == "LMH":
            qret_df['L-H'] = qret_df[llabel] - qret_df[hlabel]
        else:
            raise ValueError("Valid strategy parameters: 'HML' or 'LMH'")

        strategy_df = (qret_df.stack()
                       .reset_index()
                       .rename(columns={0: self.excess})
                       )

        return strategy_df


    def test_region_diff(self, date, strategy_df,
                         sortby, regionby,
                         minuend, substrahend,
                         model=None):
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

        groups = strategy_df.groupby(sortby, observed=False)
        test_res = groups.apply(lambda x: region_diff_nw_ttest(df=x, ret=self.excess,
                                                               regionby=regionby, minuend=minuend, substrahend=substrahend,
                                                               model_cols=model_cols, maxlags=self.maxlags))

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


    def get_alphas_region_diff(self, date, strategy_df,
                               sortby, regionby, region_strategy,
                               alpha_models, **kwargs):

        labels = strategy_df[regionby].unique()
        hlabel, llabel = labels.max(), labels.min()

        if region_strategy == "HML":
            minuend, substrahend = hlabel, llabel
            self.notes.append(f"{regionby} strategy: high minus low")
        elif region_strategy == "LMH":
            minuend, substrahend = llabel, hlabel
            self.notes.append(f"{regionby} strategy: low minus high")
        else:
            raise ValueError("Valid strategy parameters: 'HML' or 'LMH'")

        means_ls = []
        tstats_ls = []
        for n, model in enumerate(alpha_models):
            test_res, model_cols = self.test_region_diff(date=date, strategy_df=strategy_df,
                                                         sortby=sortby, regionby=regionby,
                                                         minuend=minuend,substrahend=substrahend,
                                                         model=model)

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


    def orientation_adjust(self, orientation, sortby, regionby):
        if orientation == "vertical":
            self.hhead = f"{regionby} strategy"
            self.vhead = f"{sortby}"
        elif orientation == "horizontal":
            self.means = self.means.T
            self.tstats = self.tstats.T

            self.hhead = f"{sortby}"
            self.vhead = f"{regionby} strategy"
