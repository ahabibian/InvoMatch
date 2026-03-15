from invomatch.domain.models import Invoice,Payment

def match(invoice:Invoice,payments:list[Payment]):
    for p in payments:
        if p.amount == invoice.amount:
            return {'status':'matched','payment_id':p.id}
    return {'status':'unmatched'}