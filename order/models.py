from django.db import models
from django.db.models.base import Model

# Create your models here.

class RegisterPromConfig(models.Model):
    name = models.CharField(max_length=64, null=True)
    code = models.CharField(max_length=64, null=True)
    category_id = models.IntegerField(null=True)
    prom_3m_id = models.IntegerField(null=True)
    base_score = models.FloatField(null=True)
    score_weight = models.FloatField(null=True)
    base_quantity = models.FloatField(null=True)
    quantity_weight = models.FloatField(null=True)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = 'register_prom_config'

class RegisterOrder(models.Model):
    register_3m_order_id = models.IntegerField(null=False)
    c3_id = models.IntegerField(null=True)
    c4_id = models.IntegerField(null=True)
    category_id = models.IntegerField(null=False)
    registor_code = models.CharField(max_length=64)
    registor_name = models.CharField(max_length=64)
    create_date = models.DateTimeField(auto_now_add=False, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=False)

    class Meta:
        db_table = 'cm_register_order'

class RegisterOrderExtendRuralUrban(models.Model):
    register_order_id = models.IntegerField(null=True)
    register_3m_order_id = models.IntegerField(null=False)
    prom_id = models.IntegerField(null=False)
    is_main_acc_num_new_flag = models.IntegerField(null=False,default=0)
    is_main_broadband_new_flag = models.IntegerField(null=False,default=0)
    is_tykj_flag = models.IntegerField(null=False,default=0)
    is_211_flag = models.IntegerField(null=False,default=0)
    score = models.FloatField(null=False, default=0)
    create_date = models.DateTimeField(auto_now_add=False, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=False)

    class Meta:
        db_table = 'ce_register_order_extend_rural_and_urban'

class RegisterOrderExtendBusinessAndEnterprise(Model):
    register_order_id = models.IntegerField(null=True)
    register_3m_order_id = models.IntegerField(null=False)
    prom_id = models.IntegerField(null=False)
    is_tykj_flag = models.IntegerField(null=False,default=0)
    is_211_flag = models.IntegerField(null=False,default=0)
    monthly_fee = models.FloatField(null=False, default=0)
    number_of_users = models.IntegerField(null=False, default=0)
    score = models.FloatField(null=False, default=0)
    create_date = models.DateTimeField(auto_now_add=False, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=False)

    class Meta:
        db_table = 'ce_register_order_extend_business_enterprise'

class RegisterOrderExtendExistingCustomer(models.Model):
    register_order_id = models.IntegerField(null=True)
    register_3m_order_id = models.IntegerField(null=False)
    prom_id = models.IntegerField(null=False)
    business_type = models.IntegerField(null=True)
    sales_type = models.IntegerField(null=True)
    business_content = models.IntegerField(null=True)
    score = models.FloatField(null=False, default=0)
    create_date = models.DateTimeField(auto_now_add=False, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=False)

    class Meta:
        db_table = 'ce_register_order_extend_existing_customer'
