#include <iostream>
#include <string>
#include <stack>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <thread>
#include <future>
#include <cstdlib>

int NUM_THREADS = 1;

enum class ItemType {
    Numeric,
    Operator_ADD,
    Operator_SUB,
    Operator_MUL,
    Operator_DIV,
};

class Item {
public:
    Item(char o): op_(o) {
        switch (o) {
            case '+': tp_ = ItemType::Operator_ADD; break;
            case '-': tp_ = ItemType::Operator_SUB; break;
            case '*': tp_ = ItemType::Operator_MUL; break;
            default: tp_ = ItemType::Operator_DIV; break;
        }
    }

    Item(int n): number_(n), tp_(ItemType::Numeric) {}

    std::string to_string() const {
        if(tp_==ItemType::Numeric) return std::to_string(number_);
        return std::string(1, op_);
    }

    int number() const {
        return number_;
    }

    bool is_number() const {
        return tp_ == ItemType::Numeric;
    }

    ItemType type() const {
        return tp_;
    }

    bool try_operator(double a, double b, double& out) const {
        if(tp_==ItemType::Numeric) {
            return false;
        }

        if(tp_==ItemType::Operator_ADD) {
            out = a + b;
            return true;
        }

        if(tp_==ItemType::Operator_SUB) {
            out = a - b;
            return true;
        }

        if(tp_==ItemType::Operator_MUL) {
            out = a * b;
            return true;
        }

        // DIV
        if(b==0) return false;

        out = a / b;
        return true;
    }

    bool operator < (const Item& rhs) const {
        return number_ < rhs.number_;
    }

    bool operator >= (const Item& rhs) const {
        return !(*this < rhs);
    }

private:
    int number_ = 0;
    char op_;
    ItemType tp_;
};


//void output(const std::vector<Item*>& xx) {
//    std::cout << "OUTPUT" << std::endl;
//    for(auto* x: xx) {
//        std::cout << x->to_string() << " ";
//    }
//    std::cout << std::endl;
//
//}


class SuffixFormula {
public:
    bool push(Item* item) {
        if(!invalid_) return false;

        sequence_.push_back(item);

        if(item->is_number()) {
            stack_.push(static_cast<double>(item->number()));
            return true;
        }

        if(stack_.size() < 2) {
            invalid_ = false;
            return false;
        }

        auto n1 = stack_.top();
        stack_.pop();
        auto n2 = stack_.top();
        stack_.pop();

        double n3 = 0;

        invalid_ = item->try_operator(n2, n1, n3);
        if(invalid_) {
            stack_.push(n3);
            op_amount_++;
        }

        return invalid_;
    }

    bool invalid() const {
        return invalid_;
    }

    double value() const {
        return stack_.top();
    }

    void to_normalize(std::vector<Item*>& result) {
        for(Item* item: sequence_) {
            result.push_back(item);
        }

        normalize_exchange(result);
        normalize_same_op(result, ItemType::Operator_ADD);
        normalize_same_op(result, ItemType::Operator_MUL);
        normalize_exchange_special(result, ItemType::Operator_SUB);
        normalize_exchange_special(result, ItemType::Operator_DIV);
    }

    std::string to_infix() {
        std::vector<Item*> sequence;
        to_normalize(sequence);

        std::vector<std::string> results;
        for(auto* item: sequence) {
            results.push_back(item->to_string());
        }

        while (results.size()>1) {
            for(size_t index=0; index<results.size(); index++) {
                if(results[index] == "+" || results[index] == "-" || results[index] == "*" || results[index] == "/") {
                    std::string res;
                    res += "(";
                    res += results[index-2];
                    res += " ";
                    res += results[index];
                    res += " ";
                    res += results[index-1];
                    res += ")";

                    results.erase(results.begin()+index-2);
                    results.erase(results.begin()+index-2);
                    results.erase(results.begin()+index-2);

                    results.insert(results.begin()+index-2, res);
                    break;
                }
            }
        }

        return results[0].substr(1, results[0].length()-2);
    }

private:
    std::stack<double> stack_;
    std::vector<Item*> sequence_;
    size_t op_amount_ = 0;
    bool invalid_ = true;

    size_t find_sub_sequence_index(const std::vector<Item*>& sequence, size_t pos) {
        int num_amount = 0;
        int op_amount = 0;

        while(pos>=0) {
            if(sequence[pos]->is_number()) num_amount++;
            else op_amount++;

            if(num_amount == op_amount+1) return pos;
            pos--;
        }

        return 0;
    }

    void normalize_exchange(std::vector<Item*>& sequence) {
        size_t length = sequence.size();
        for(size_t index=2; index<=length-1; index++) {
            if (sequence[index]->type() == ItemType::Operator_ADD || sequence[index]->type() == ItemType::Operator_MUL) {
                Item* item1 = sequence[index-2];
                Item* item2 = sequence[index-1];

                if(!item2->is_number()) {
                    auto sub_index_2 = find_sub_sequence_index(sequence, index-1);
                    if(sequence[sub_index_2-1]->is_number()) continue;

                    auto sub_index_1 = find_sub_sequence_index(sequence, sub_index_2-1);
                    if(*sequence[sub_index_2] >= *sequence[sub_index_1]) continue;

                    std::vector<Item*> sub_seq_2;
                    auto sub_seq_2_length = index-1-sub_index_2+1;
                    sub_seq_2.reserve(sub_seq_2_length);
                    auto iter = sequence.begin();
                    for(size_t i=0; i<sub_seq_2_length; i++) {
                        sub_seq_2.push_back(sequence[sub_index_2]);
                        sequence.erase(iter+sub_index_2);
                    }

                    sequence.insert(sequence.begin()+sub_index_1, sub_seq_2.begin(), sub_seq_2.end());
                    continue;
                }

                if(item1->is_number()) {
                    if(*item2 < * item1) {
                        sequence[index-2] = item2;
                        sequence[index-1] = item1;
                    }

                    continue;
                }

                auto sub_index = find_sub_sequence_index(sequence, index);
                sequence.erase(sequence.begin()+index-1);
                sequence.insert(sequence.begin()+sub_index, item2);
            }
        }
    }

    void normalize_exchange_special(std::vector<Item*>& sequence, ItemType op_tp) {
        size_t length = sequence.size();
        for(size_t index=0; index<length; index++) {
            if(index+4 > length-1) return;

            auto a = sequence[index];
            auto b = sequence[index+1];
            auto c = sequence[index+2];
            auto d = sequence[index+3];
            auto e = sequence[index+4];

            if(a->is_number() && b->is_number() && c->type() == op_tp && d->is_number() && e->type() == op_tp) {
                if(*d < *b) {
                    sequence[index+1] = d;
                    sequence[index+3] = b;
                }
            }
        }
    }

    void normalize_same_op(std::vector<Item*>& sequence, ItemType op_tp) {
        std::vector<size_t> op_indexes;
        std::vector<Item*> op_items;

        for(size_t i=0; i<sequence.size(); i++) {
            if(sequence[i]->type() == op_tp) {
                op_indexes.push_back(i);
                op_items.push_back(sequence[i]);
            }
        }

        if(op_indexes.size()!=op_amount_) return;

        for(size_t i=0; i<op_amount_; i++) {
            sequence.erase(sequence.begin() + op_indexes[i] - i);
        }

        auto cmp = [](Item* a, Item* b) {return *a < *b;};
        std::sort(sequence.begin(), sequence.end(), cmp);
        sequence.insert(sequence.end(), op_items.begin(), op_items.end());
    }
};


class Operators {
public:
    Operators(int amount): amount_(amount) {
        for(int i=0; i<amount; i++) {
            levels_[i] = 0;
        }
    }

    ~Operators() {
        for(auto* item: operators_) delete item;
    }

    std::vector<Item*> get() {
        std::vector<Item*> opts;
        if(levels_[0] > 3) return opts;

        for(int i=0; i<amount_; i++) {
            opts.push_back(operators_[levels_[i]]);
        }

        levels_[amount_-1] += 1;

        for(int i=amount_-1; i>0; i--) {
            if(levels_[i] > 3) {
                levels_[i] = 0;
                levels_[i-1] += 1;
            }
        }

        return opts;
    }

private:
    int amount_;
    const std::vector<Item*> operators_{new Item('+'), new Item('-'), new Item('*'), new Item('/')};
    std::map<int, int> levels_;
};

bool is_invalid_sequence(const std::vector<Item*>& seq) {
    int number_amount = 0;
    int op_amount = 0;

    for(auto* item: seq) {
        if(item->is_number()) number_amount++;
        else op_amount++;

        if(op_amount >= number_amount) return false;
    }

    return true;
}

void find(int target, std::vector<Item*> numbers, std::vector<std::vector<Item*>> ops, std::promise<std::set<std::string>>& p) {
    std::set<std::string> results;
    std::cout << "thread: " << std::this_thread::get_id() << ", ops len, " << ops.size() << std::endl;
    for(auto& op: ops) {
        std::vector<Item*> items;
        items.insert(items.end(), numbers.begin(), numbers.end());
        items.insert(items.end(), op.begin(), op.end());

//        auto cmd = [](Item* a, Item* b) {return *a < *b;};

        std::sort(items.begin(), items.end());
        do {
            if(!is_invalid_sequence(items)) continue;

            SuffixFormula sf;
            for(Item* item: items) {
                if(!sf.push(item)) break;
            }

            if(!sf.invalid()) continue;

            double x = sf.value() - target;
            if(x >= -1e-3 && x <= 1e-3) {
                results.insert(sf.to_infix());
            }

        } while (std::next_permutation(items.begin(), items.end()));

    }
    p.set_value(results);

}

int main(int argc, char* argv[]) {
    int target, amount, number;
    std::vector<Item*> numbers;

    target = std::atoi(argv[1]);
    amount = argc - 2;

    for(int i=1; i<=amount; i++) {
        number = std::atoi(argv[1+i]);
        numbers.push_back(new Item(number));
    }

    Operators ops(amount-1);
    std::vector<std::vector<Item*>> all_ops;
    while (true) {
        auto op = ops.get();
        if(op.empty()) break;

        all_ops.push_back(op);
    }

    std::set<std::string> results;

    size_t step = all_ops.size() / NUM_THREADS;

    std::vector<std::vector<Item*>> splitted_ops[NUM_THREADS];
    for(int i=0; i<NUM_THREADS; i++) {
        splitted_ops[i].insert(splitted_ops[i].end(), all_ops.begin()+step*i, all_ops.begin()+step*(i+1));
    }

    splitted_ops[NUM_THREADS-1].insert(splitted_ops[NUM_THREADS-1].end(), all_ops.begin()+step*NUM_THREADS, all_ops.end());

    std::promise<std::set<std::string>> p[NUM_THREADS];
    std::future<std::set<std::string>> f[NUM_THREADS];
    std::thread ts[NUM_THREADS];

    for(int i=0; i<NUM_THREADS; i++) {
        f[i] = p[i].get_future();
        ts[i] = std::thread(find, target, numbers, splitted_ops[i], std::ref(p[i]));
    }

    std::cout << "wait thread ..." << std::endl;
    for(int i=0; i<NUM_THREADS; i++) {
        ts[i].join();
        auto xx = f[i].get();

        results.insert(xx.begin(), xx.end());
    }

    if(results.empty()) {
        std::cout << "no results" << std::endl;
    } else {
        for(auto& s: results) {
            std::cout << s << " = " << target << std::endl;
        }
    }

    for(auto* item: numbers) delete item;

    return 0;
}