from datetime import datetime, UTC

# Peewee imports
import peewee as pw


# Database will be initialized in DatabaseManager
database = pw.SqliteDatabase(None)


# Base model for all models
class DBBaseModel(pw.Model):
    class Meta:
        database = database


# ORM Models
class DBCountry(DBBaseModel):
    id = pw.AutoField(primary_key=True)
    name = pw.CharField(max_length=100, null=False)
    iso3 = pw.CharField(max_length=3, null=True)
    numeric_code = pw.CharField(max_length=3, null=True)
    iso2 = pw.CharField(max_length=2, null=True)
    phonecode = pw.CharField(max_length=255, null=True)
    capital = pw.CharField(max_length=255, null=True)
    currency = pw.CharField(max_length=255, null=True)
    currency_name = pw.CharField(max_length=255, null=True)
    currency_symbol = pw.CharField(max_length=255, null=True)
    tld = pw.CharField(max_length=255, null=True)
    native = pw.CharField(max_length=255, null=True)
    region = pw.CharField(max_length=255, null=True)
    region_id = pw.IntegerField(null=True)
    subregion = pw.CharField(max_length=255, null=True)
    subregion_id = pw.IntegerField(null=True)
    nationality = pw.CharField(max_length=255, null=True)
    timezones = pw.TextField(null=True)
    translations = pw.TextField(null=True)
    latitude = pw.FloatField(null=True)
    longitude = pw.FloatField(null=True)
    emoji = pw.CharField(max_length=191, null=True)
    emojiU = pw.CharField(max_length=191, null=True)
    created_at = pw.DateTimeField(null=True)
    updated_at = pw.DateTimeField(default=lambda: datetime.now(UTC))
    flag = pw.BooleanField(default=True)
    wikiDataId = pw.CharField(max_length=255, null=True)

    class Meta:
        table_name = 'countries'


class DBRegion(DBBaseModel):
    id = pw.AutoField(primary_key=True)
    name = pw.CharField(max_length=100, null=False)
    translations = pw.TextField(null=True)
    created_at = pw.DateTimeField(null=True)
    updated_at = pw.DateTimeField(default=datetime.now(UTC))
    flag = pw.BooleanField(default=True)
    wikiDataId = pw.CharField(max_length=255, null=True)

    class Meta:
        table_name = 'regions'


class DBSubregion(DBBaseModel):
    id = pw.AutoField(primary_key=True)
    name = pw.CharField(max_length=100, null=False)
    translations = pw.TextField(null=True)
    region_id = pw.ForeignKeyField(DBRegion, column_name='region_id', null=False)
    created_at = pw.DateTimeField(null=True)
    updated_at = pw.DateTimeField(default=datetime.now(UTC))
    flag = pw.BooleanField(default=True)
    wikiDataId = pw.CharField(max_length=255, null=True)

    class Meta:
        table_name = 'subregions'


class DBState(DBBaseModel):
    id = pw.AutoField(primary_key=True)
    name = pw.CharField(max_length=255, null=False)
    country = pw.ForeignKeyField(
        DBCountry, column_name='country_id', backref='states', null=False
    )
    country_code = pw.CharField(max_length=2, null=False)
    fips_code = pw.CharField(max_length=255, null=True)
    iso2 = pw.CharField(max_length=255, null=True)
    type = pw.CharField(max_length=191, null=True)
    level = pw.IntegerField(null=True)
    parent_id = pw.IntegerField(null=True)
    latitude = pw.FloatField(null=True)
    longitude = pw.FloatField(null=True)
    created_at = pw.DateTimeField(null=True)
    updated_at = pw.DateTimeField(default=datetime.now(UTC))
    flag = pw.BooleanField(default=True)
    wikiDataId = pw.CharField(max_length=255, null=True)

    class Meta:
        table_name = 'states'


class DBCity(DBBaseModel):
    id = pw.AutoField(primary_key=True)
    name = pw.CharField(max_length=255, null=False)
    state = pw.ForeignKeyField(
        DBState, column_name='state_id', backref='cities', null=False
    )
    state_code = pw.CharField(max_length=255, null=False)
    country = pw.ForeignKeyField(
        DBCountry, column_name='country_id', backref='cities', null=False
    )
    country_code = pw.CharField(max_length=2, null=False)
    latitude = pw.FloatField(null=False)
    longitude = pw.FloatField(null=False)
    created_at = pw.DateTimeField(default=datetime.now(UTC))
    updated_at = pw.DateTimeField(default=datetime.now(UTC))
    flag = pw.BooleanField(default=True)
    wikiDataId = pw.CharField(max_length=255, null=True)

    class Meta:
        table_name = 'cities'
