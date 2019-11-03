from model_bakery import baker


def gen_cnpj():
    return '89.889.920/0001-16'


baker.generators.add('localflavor.br.models.BRCNPJField', gen_cnpj)
