from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Role(models.Model):
    name = models.CharField(null=False, max_length=64)
    category = models.IntegerField(null=False)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = 'cm_role'

class Organization(models.Model):
    name = models.CharField(max_length=128)
    c3_id = models.IntegerField(null=True)
    c4_id = models.IntegerField(null=True)
    org_level = models.IntegerField(null=True)
    parent_id = models.IntegerField(null=False)
    org_3m_id = models.IntegerField(null=True)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = 'cm_organization'
    
    @property
    def c3_name(self):
        if self.c3_id:
            try:
                return Organization.objects.get(id=self.c3_id).name
            except Organization.DoesNotExist as e:
                return None
            except Organization.MultipleObjectsReturned as e:
                return None
    @property
    def c4_name(self):
        if self.c4_id:
            try:
                return Organization.objects.get(id=self.c4_id).name
            except Organization.DoesNotExist as e:
                return None
            except Organization.MultipleObjectsReturned as e:
                return None
    @property
    def org_tree(self):
        _org_tree = ''
        if self.c3_id:
            _org_tree = _org_tree  + self.c3_name
        if self.c4_id:
            _org_tree = _org_tree + ' ' + self.c4_name
        if _org_tree == '':
            return self.name
        else:
            return _org_tree + ' ' + self.name

class Staff(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    id_number = models.CharField(max_length=32, null=True)
    contact = models.CharField(max_length=16)
    wx_open_id = models.CharField(max_length=128, null=True)
    wx_nick_name = models.CharField(max_length=128, null=True)
    org_id = models.IntegerField(null=True)
    staff_3m_id = models.IntegerField(null=True)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    role = models.ManyToManyField(Role)
    
    class Meta:
        db_table = 'cm_staff'
    @property
    def roles(selef):
        pass
    
    def create_user(self):
        if self.contact and self.wx_open_id:
            try:
                u = User.objects.get(username=self.contact)
                u.set_password(self.wx_open_id)
                u.save()
                self.user = u
                self.save()
                return 'success'
            except User.DoesNotExist as e:
                u = User()
                u.username = self.contact
                u.set_password(self.wx_open_id)
                u.save()
                self.user = u
                self.save()
                return 'success'
            except User.MultipleObjectsReturned as e:
                return 'fail'
        else:
            return 'fail'
    
    def organization(self):
        try:
            return Organization.objects.get(id=self.org_id)
        except Organization.DoesNotExist as e:
            return None
    
    def activate_user(self):
        if not self.user.is_active:
            self.user.is_active = True

    def deactivate_user(self):
        if self.user.is_active:
            self.user.is_active = False

class MarketOrganization(models.Model):
    name = models.CharField(max_length=64, null=True)
    parent_id = models.IntegerField(null=True)
    org_id = models.IntegerField(null=True)
    c3_id = models.IntegerField(null=True)
    c4_id = models.IntegerField(null=True)
    c5_id = models.IntegerField(null=True)
    market_org_3m_id = models.IntegerField(null=True)
    market_org_3m_parent_id = models.IntegerField(null=True)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = 'cm_market_organization'

class Dict(models.Model):
    '字典'
    module = models.CharField(null=False, max_length=32)
    model = models.CharField(null=False, max_length=32)
    attribute = models.CharField(null=False, max_length=32)
    value = models.IntegerField(null=False)
    definition = models.CharField(null=False, max_length=32)
    code = models.CharField(null=True, max_length=32, default='')
    description = models.CharField(null=True, max_length=128)
    created_by = models.IntegerField(null=False)
    created_date = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_dict'
        ordering = ['value']