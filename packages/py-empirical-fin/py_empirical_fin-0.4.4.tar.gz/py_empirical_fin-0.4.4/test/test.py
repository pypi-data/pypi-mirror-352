from empiricalfin import sorting
import pandas as pd

panel = pd.read_csv("./data/panel_dropna.csv",
                    dtype={"code": str},
                    parse_dates=["month"])
                    
                    
rf_df = pd.read_csv("./data/单位为百分比_1990-04-15 至 2023-12-31.csv",
                    usecols=["Clsdt", "Nrrmtdt"],
                    parse_dates=["Clsdt"])
rf_df = rf_df.rename(columns={"Clsdt": "month", "Nrrmtdt": "rf"})
# 将无风险利率转换为小数
rf_df["rf"] = rf_df["rf"] / 100

ff3 = pd.read_csv("./data/1990-12 至 2023-12.csv", 
                  usecols=["MarkettypeID", "TradingMonth", 
                           "RiskPremium1", "SMB1", "HML1"],
                  parse_dates=["TradingMonth"]
                 )
ff3["TradingMonth"] = ff3["TradingMonth"] + pd.offsets.MonthEnd(0)
ff3 = ff3.rename(columns={"TradingMonth": "month",
                          "RiskPremium1": "mkt_premium",
                          "SMB1": "SMB",
                          "HML1": "HML"})
ff3 = ff3.query("month <= '2020-08-31' and MarkettypeID == 'P9709' or month >= '2020-09-30' and MarkettypeID == 'P9706'")
ff3 = ff3.drop(columns="MarkettypeID")

ch3 = pd.read_excel("./data/CH3_factors_monthly_202405.xlsx",
                   parse_dates=["mnthdt"])
ch3["MKT"] = ch3["mktrf"] - ch3["rf_mon"]
ch3 = ch3.drop(columns=["rf_mon", "mktrf"]).rename(columns={"mnthdt": "month"})

panel = panel.rename(columns={"TURN": "FC2", "MAX": "FC1", "ret_daily": "ret"})
panel = panel.reindex(columns=["code", "month", "ret",
                               "FC1", "FC2", "SIZE"])

region_data = pd.read_csv("./data/region_cicsi.csv",
                          parse_dates=['month'])

# ss = sorting.SingleSorting(panel, sortby="FC1", nq=5,
#                            date="month", ret="ret",
#                            mkt_cap="SIZE")
# results = ss.single(vw=False)
# results.summary(rf_df=rf_df, rf="rf", show_t=True, show_stars=True, layout="default", raw_ret=False, pct_sign=True,
#                alpha_models=[ff3, ch3], output_path="Single_out_true_strategy_excess_alpha_pct.docx")
# results = ss.single(vw=True)

# ds = sorting.DoubleSorting(panel, sortbys=["FC1", "FC2"],
#                            nqs=[5, 5], date="month", ret="ret",
#                            mkt_cap="SIZE")
# result = ds.independent(vw=False)
# result.summary(rf_df=rf_df, rf="rf", raw_ret=True, layout='reverse', pct_sign=False,
#                alpha_models=[ff3, ch3], output_path=None)

rs = sorting.RegionSorting(panel, region_data,
                           sortby="FC2", nq=5,
                           nregion=2, date="month", ret="ret",
                           mkt_cap="SIZE")
result = rs.region(vw=True)
result.summary(rf_df=rf_df, rf="rf", raw_ret=False, layout='default', pct_sign=False,
               sort_strategy='HML', region_strategy='HML',
               show_t=True, alpha_models=[ff3, ch3], output_path='Region_maxlags_default.docx')