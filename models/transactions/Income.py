import operator

from models.transactions.Transaction import Transaction


class Income(Transaction):
    def get_expanses(self):
        from models.transactions.Expense import Expanse
        from models.transactions.Bid import Bid
        exp = Expanse.select().join(Bid).where(Bid.parent_income == self).order_by(Expanse.created_at)
        exp = list(exp)

        return exp
    def get_expanses_amount(self):
        return sum(map(operator.attrgetter('amount'), self.get_expanses()))
    def get_expanses_text(self):
        exp=self.get_expanses()
        text = ''
        sums=self.amount
        for tr2 in exp:
            sums-=tr2.amount
            text += f'\n\t\tТрата -{tr2.amount} от:"{tr2.author.name}" {tr2.created_at.strftime("%d/%m/%Y, %H:%M")} Б-с:{sums} {tr2.description} \n'
        return text