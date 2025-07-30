import pandas

def qcut_with_exception(series, q, labels):
    try:
        return pandas.qcut(series, q=q, labels=labels)
    # if failed, use percentile rank
    except ValueError:
        rank_series = series.rank(ascending=True, method='first',
                                  na_option='keep', pct=True)
        return pandas.qcut(rank_series, q=q, labels=labels)


def ew_ret(data, ret_col, **kwargs):
    '''
    Equal weighted return
    '''
    ret = data[ret_col]

    ew_ret = ret.mean()
    return ew_ret 


def vw_ret(data, ret_col, mkt_cap_col, **kwargs):
    '''
    Value weighted return
    '''
    ret = data[ret_col]
    mkt_cap = data[mkt_cap_col]

    weights = mkt_cap / mkt_cap.sum()
    vw_ret = (ret * weights).sum()
    return vw_ret


def remove_items(remove, array):
    return list(array[~array.isin(remove)])


def decimal(value, decimal):
    fmt = "{" + f":.{decimal}f" + "}"
    return fmt.format(value)   


def asterisk(p):
    if p < 0.01:
        return "***"
    elif p < 0.05:
        return "**"
    elif p < 0.1:
        return "*"
    else:
        return ""