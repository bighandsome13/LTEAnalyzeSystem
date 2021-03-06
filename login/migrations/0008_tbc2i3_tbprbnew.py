# Generated by Django 3.1.7 on 2021-05-28 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0007_tbc2inew'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbC2I3',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('a_sector', models.CharField(db_column='A_SECTOR', max_length=50)),
                ('b_sector', models.CharField(db_column='B_SECTOR', max_length=50)),
                ('c_sector', models.CharField(db_column='C_SECTOR', max_length=50)),
            ],
            options={
                'db_table': 'tbC2I3',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Tbprbnew',
            fields=[
                ('date', models.DateTimeField(db_column='Date')),
                ('enodeb_name', models.CharField(db_column='ENODEB_NAME', max_length=255)),
                ('sector_description', models.CharField(db_column='SECTOR_DESCRIPTION', max_length=255)),
                ('sector_name', models.CharField(db_column='SECTOR_NAME', max_length=255, primary_key=True, serialize=False)),
                ('avr_noise_prb0', models.IntegerField(db_column='AVR_NOISE_PRB0')),
                ('avr_noise_prb1', models.IntegerField(db_column='AVR_NOISE_PRB1')),
                ('avr_noise_prb2', models.IntegerField(db_column='AVR_NOISE_PRB2')),
                ('avr_noise_prb3', models.IntegerField(db_column='AVR_NOISE_PRB3')),
                ('avr_noise_prb4', models.IntegerField(db_column='AVR_NOISE_PRB4')),
                ('avr_noise_prb5', models.IntegerField(db_column='AVR_NOISE_PRB5')),
                ('avr_noise_prb6', models.IntegerField(db_column='AVR_NOISE_PRB6')),
                ('avr_noise_prb7', models.IntegerField(db_column='AVR_NOISE_PRB7')),
                ('avr_noise_prb8', models.IntegerField(db_column='AVR_NOISE_PRB8')),
                ('avr_noise_prb9', models.IntegerField(db_column='AVR_NOISE_PRB9')),
                ('avr_noise_prb10', models.IntegerField(db_column='AVR_NOISE_PRB10')),
                ('avr_noise_prb11', models.IntegerField(db_column='AVR_NOISE_PRB11')),
                ('avr_noise_prb12', models.IntegerField(db_column='AVR_NOISE_PRB12')),
                ('avr_noise_prb13', models.IntegerField(db_column='AVR_NOISE_PRB13')),
                ('avr_noise_prb14', models.IntegerField(db_column='AVR_NOISE_PRB14')),
                ('avr_noise_prb15', models.IntegerField(db_column='AVR_NOISE_PRB15')),
                ('avr_noise_prb16', models.IntegerField(db_column='AVR_NOISE_PRB16')),
                ('avr_noise_prb17', models.IntegerField(db_column='AVR_NOISE_PRB17')),
                ('avr_noise_prb18', models.IntegerField(db_column='AVR_NOISE_PRB18')),
                ('avr_noise_prb19', models.IntegerField(db_column='AVR_NOISE_PRB19')),
                ('avr_noise_prb20', models.IntegerField(db_column='AVR_NOISE_PRB20')),
                ('avr_noise_prb21', models.IntegerField(db_column='AVR_NOISE_PRB21')),
                ('avr_noise_prb22', models.IntegerField(db_column='AVR_NOISE_PRB22')),
                ('avr_noise_prb23', models.IntegerField(db_column='AVR_NOISE_PRB23')),
                ('avr_noise_prb24', models.IntegerField(db_column='AVR_NOISE_PRB24')),
                ('avr_noise_prb25', models.IntegerField(db_column='AVR_NOISE_PRB25')),
                ('avr_noise_prb26', models.IntegerField(db_column='AVR_NOISE_PRB26')),
                ('avr_noise_prb27', models.IntegerField(db_column='AVR_NOISE_PRB27')),
                ('avr_noise_prb28', models.IntegerField(db_column='AVR_NOISE_PRB28')),
                ('avr_noise_prb29', models.IntegerField(db_column='AVR_NOISE_PRB29')),
                ('avr_noise_prb30', models.IntegerField(db_column='AVR_NOISE_PRB30')),
                ('avr_noise_prb31', models.IntegerField(db_column='AVR_NOISE_PRB31')),
                ('avr_noise_prb32', models.IntegerField(db_column='AVR_NOISE_PRB32')),
                ('avr_noise_prb33', models.IntegerField(db_column='AVR_NOISE_PRB33')),
                ('avr_noise_prb34', models.IntegerField(db_column='AVR_NOISE_PRB34')),
                ('avr_noise_prb35', models.IntegerField(db_column='AVR_NOISE_PRB35')),
                ('avr_noise_prb36', models.IntegerField(db_column='AVR_NOISE_PRB36')),
                ('avr_noise_prb37', models.IntegerField(db_column='AVR_NOISE_PRB37')),
                ('avr_noise_prb38', models.IntegerField(db_column='AVR_NOISE_PRB38')),
                ('avr_noise_prb39', models.IntegerField(db_column='AVR_NOISE_PRB39')),
                ('avr_noise_prb40', models.IntegerField(db_column='AVR_NOISE_PRB40')),
                ('avr_noise_prb41', models.IntegerField(db_column='AVR_NOISE_PRB41')),
                ('avr_noise_prb42', models.IntegerField(db_column='AVR_NOISE_PRB42')),
                ('avr_noise_prb43', models.IntegerField(db_column='AVR_NOISE_PRB43')),
                ('avr_noise_prb44', models.IntegerField(db_column='AVR_NOISE_PRB44')),
                ('avr_noise_prb45', models.IntegerField(db_column='AVR_NOISE_PRB45')),
                ('avr_noise_prb46', models.IntegerField(db_column='AVR_NOISE_PRB46')),
                ('avr_noise_prb47', models.IntegerField(db_column='AVR_NOISE_PRB47')),
                ('avr_noise_prb48', models.IntegerField(db_column='AVR_NOISE_PRB48')),
                ('avr_noise_prb49', models.IntegerField(db_column='AVR_NOISE_PRB49')),
                ('avr_noise_prb50', models.IntegerField(db_column='AVR_NOISE_PRB50')),
                ('avr_noise_prb51', models.IntegerField(db_column='AVR_NOISE_PRB51')),
                ('avr_noise_prb52', models.IntegerField(db_column='AVR_NOISE_PRB52')),
                ('avr_noise_prb53', models.IntegerField(db_column='AVR_NOISE_PRB53')),
                ('avr_noise_prb54', models.IntegerField(db_column='AVR_NOISE_PRB54')),
                ('avr_noise_prb55', models.IntegerField(db_column='AVR_NOISE_PRB55')),
                ('avr_noise_prb56', models.IntegerField(db_column='AVR_NOISE_PRB56')),
                ('avr_noise_prb57', models.IntegerField(db_column='AVR_NOISE_PRB57')),
                ('avr_noise_prb58', models.IntegerField(db_column='AVR_NOISE_PRB58')),
                ('avr_noise_prb59', models.IntegerField(db_column='AVR_NOISE_PRB59')),
                ('avr_noise_prb60', models.IntegerField(db_column='AVR_NOISE_PRB60')),
                ('avr_noise_prb61', models.IntegerField(db_column='AVR_NOISE_PRB61')),
                ('avr_noise_prb62', models.IntegerField(db_column='AVR_NOISE_PRB62')),
                ('avr_noise_prb63', models.IntegerField(db_column='AVR_NOISE_PRB63')),
                ('avr_noise_prb64', models.IntegerField(db_column='AVR_NOISE_PRB64')),
                ('avr_noise_prb65', models.IntegerField(db_column='AVR_NOISE_PRB65')),
                ('avr_noise_prb66', models.IntegerField(db_column='AVR_NOISE_PRB66')),
                ('avr_noise_prb67', models.IntegerField(db_column='AVR_NOISE_PRB67')),
                ('avr_noise_prb68', models.IntegerField(db_column='AVR_NOISE_PRB68')),
                ('avr_noise_prb69', models.IntegerField(db_column='AVR_NOISE_PRB69')),
                ('avr_noise_prb70', models.IntegerField(db_column='AVR_NOISE_PRB70')),
                ('avr_noise_prb71', models.IntegerField(db_column='AVR_NOISE_PRB71')),
                ('avr_noise_prb72', models.IntegerField(db_column='AVR_NOISE_PRB72')),
                ('avr_noise_prb73', models.IntegerField(db_column='AVR_NOISE_PRB73')),
                ('avr_noise_prb74', models.IntegerField(db_column='AVR_NOISE_PRB74')),
                ('avr_noise_prb75', models.IntegerField(db_column='AVR_NOISE_PRB75')),
                ('avr_noise_prb76', models.IntegerField(db_column='AVR_NOISE_PRB76')),
                ('avr_noise_prb77', models.IntegerField(db_column='AVR_NOISE_PRB77')),
                ('avr_noise_prb78', models.IntegerField(db_column='AVR_NOISE_PRB78')),
                ('avr_noise_prb79', models.IntegerField(db_column='AVR_NOISE_PRB79')),
                ('avr_noise_prb80', models.IntegerField(db_column='AVR_NOISE_PRB80')),
                ('avr_noise_prb81', models.IntegerField(db_column='AVR_NOISE_PRB81')),
                ('avr_noise_prb82', models.IntegerField(db_column='AVR_NOISE_PRB82')),
                ('avr_noise_prb83', models.IntegerField(db_column='AVR_NOISE_PRB83')),
                ('avr_noise_prb84', models.IntegerField(db_column='AVR_NOISE_PRB84')),
                ('avr_noise_prb85', models.IntegerField(db_column='AVR_NOISE_PRB85')),
                ('avr_noise_prb86', models.IntegerField(db_column='AVR_NOISE_PRB86')),
                ('avr_noise_prb87', models.IntegerField(db_column='AVR_NOISE_PRB87')),
                ('avr_noise_prb88', models.IntegerField(db_column='AVR_NOISE_PRB88')),
                ('avr_noise_prb89', models.IntegerField(db_column='AVR_NOISE_PRB89')),
                ('avr_noise_prb90', models.IntegerField(db_column='AVR_NOISE_PRB90')),
                ('avr_noise_prb91', models.IntegerField(db_column='AVR_NOISE_PRB91')),
                ('avr_noise_prb92', models.IntegerField(db_column='AVR_NOISE_PRB92')),
                ('avr_noise_prb93', models.IntegerField(db_column='AVR_NOISE_PRB93')),
                ('avr_noise_prb94', models.IntegerField(db_column='AVR_NOISE_PRB94')),
                ('avr_noise_prb95', models.IntegerField(db_column='AVR_NOISE_PRB95')),
                ('avr_noise_prb96', models.IntegerField(db_column='AVR_NOISE_PRB96')),
                ('avr_noise_prb97', models.IntegerField(db_column='AVR_NOISE_PRB97')),
                ('avr_noise_prb98', models.IntegerField(db_column='AVR_NOISE_PRB98')),
                ('avr_noise_prb99', models.IntegerField(db_column='AVR_NOISE_PRB99')),
            ],
            options={
                'db_table': 'tbprbnew',
                'managed': True,
            },
        ),
    ]
