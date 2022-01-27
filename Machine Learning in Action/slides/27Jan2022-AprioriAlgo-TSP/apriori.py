

def load_data():
    """Loads synthetic data

    Returns:
        synthetic_list: list of transactions
    """
    return [[1,3,4],[2,3,5],[1,2,3,5],[2,5]]

def create_ci1(dataset):
    """Generates candidate itemsets of length 1

    Args:
        dataset (list): list of transactions

    Returns:
        list: list of candidate itemsets of size 1
    """
    ci1 = []
    for transaction in dataset:
        for item in transaction:
            if not [item] in ci1:
                ci1.append([item])
    ci1.sort()
    return list(map(frozenset,ci1))

def scan_data(dataset, cik, min_support):
    """Scan dataset to generate support data above min_support
    Args:
        dataset (list): list of transactions
        cik (list): list of candidate itemsets of size k
        min_support (float): cutoff for support

    Returns:
        return_list (list): all frequent itemsets
        support_data (dict): support data for all frequent itemsets"""
    ci_count_dict = {}
    for transaction_id in dataset:
        for candidate in cik:
            if candidate.issubset(transaction_id):
                if candidate not in ci_count_dict: ci_count_dict[candidate] = 1
                else: ci_count_dict[candidate] += 1
    num_items = float(len(dataset))
    return_list = []
    support_data = {}
    for key in ci_count_dict:
        support = ci_count_dict[key]/num_items
        if support >= min_support:
            return_list.insert(0,key)
        support_data[key] = support
    return return_list, support_data

def apriori_candidate(lk, k):
    """Generates candidate itemsets of size k"""
    return_list = []
    len_lk = len(lk)
    for i in range(len_lk):
        for j in range(i+1, len_lk):
            l1 = list(lk[i])[:k-2]
            l2 = list(lk[j])[:k-2]
            l1.sort()
            l2.sort()
            if l1 == l2:
                return_list.append(lk[i] | lk[j])
    return return_list

def apriori_algo(dataset, min_support = 0.5):
    """Runs the apriori algorithm

    Args:
        dataset (list): list of transactions
        min_support (float, optional): cutoff for support. Defaults to 0.5.

    Returns:
        l (list): nested list of all frequent itemsets of various sizes
        support_data (dict): support data for all frequent itemsets
    """
    ci1 = create_ci1(dataset)
    D = list(map(set, dataset))
    l1, support_data = scan_data(D, ci1, min_support)
    l = [l1]
    k = 2
    while (len(l[k-2]) > 0):
        cik = apriori_candidate(l[k-2], k)
        lk, supk = scan_data(D, cik, min_support)
        support_data.update(supk)
        l.append(lk)
        k += 1
    return l, support_data

def generate_rules(l, support_data, min_confidence=0.7):
    """Generates association rules from frequent itemsets

    Args:
        l (list)): nested list of all frequent itemsets of various sizes
        support_data (dict): support data for all frequent itemsets
        min_confidence (float, optional): cutoff for confidence. Defaults to 0.7.

    Returns:
        big_rule_list (list): list of all rules
    """
    big_rule_list = []
    for i in range(1, len(l)):
        for freq_set in l[i]:
            H1 = [frozenset([item]) for item in freq_set]
            if i > 1:
                rules_from_conseq(freq_set, H1, support_data, big_rule_list, min_confidence)
            else:
                calc_confidence(freq_set, H1, support_data, big_rule_list, min_confidence)
    return big_rule_list

def calc_confidence(freq_set, itemsets, support_data, big_rule_list, min_confidence):
    """Calculates confidence for rules generated from frequent itemsets

    Args:
        freq_set (list): list frequent itemset of size k
        itemsets (list): list of candidate itemsets of size k
        support_data (dict): support data for all frequent itemsets
        big_rule_list (list): list of all rules
        min_confidence (float): cutoff for confidence

    Returns:
        pruned_itemsets: list of all rules with confidence above min_confidence
    """
    pruned_itemsets = []
    for conseq in itemsets:
        conf = support_data[freq_set]/support_data[freq_set-conseq]
        if conf >= min_confidence:
            print(freq_set-conseq, '-->', conseq, 'conf:', conf)
            big_rule_list.append((freq_set-conseq, conseq, conf))
            pruned_itemsets.append(conseq)
    return pruned_itemsets

def rules_from_conseq(freq_set, itemsets, support_data, big_rule_list, min_confidence):
    """Generates rules from frequent itemsets"""    
    m = len(itemsets[0])
    if len(freq_set) > (m + 1):
        Hmp1 = apriori_candidate(itemsets, m+1)
        Hmp1 = calc_confidence(freq_set, Hmp1, support_data, big_rule_list, min_confidence)
        if len(Hmp1) > 1:
            rules_from_conseq(freq_set, Hmp1, support_data, big_rule_list, min_confidence)
                