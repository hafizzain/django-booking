from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.response import Response
from .models import *



# @receiver(post_save, sender=SaleRecordMembership)
# def create_membership_installment(sender, instance, created, **kwargs):
#     if created and instance.installment_months:
#         # Create a single MembershipInstallments instance
#         MembershipInstallments.objects.create(
#             membership=instance,
#             paid_installment=instance.price  # Or any default value you prefer
#         )

@receiver(post_save, sender=MembershipInstallments)
def next_installment_expiry(sender, instance, created, **kwargs):
    try:
        if created:  # Check if the instance is newly created
            membership = instance.membership  # Assuming membership is the ForeignKey field in MembershipInstallments
            if membership.installment_months:
                # Assuming calculate_validity function is defined elsewhere and correctly calculates the next installment date
                next_membership_expiry = relativedelta(membership.created_at, instance.created_at).months + 1 
                membership.next_installment_date = calculate_validity(str(next_membership_expiry)+ ' months')
                total_paid_installments = MembershipInstallments.objects.filter(membership = instance.membership).count()
                membership.remaining_installments = membership.installment_months - total_paid_installments
                
                # currency_id = 
                memberhsip_instance = CurrencyPriceMembership.objects.filter(
                                                        currency_id=membership.sale_record.location.currency.id,
                                                        membership_id=membership.membership.id
                                                    ).first()
                membership.payable_amount = memberhsip_instance.price - instance.paid_installment
                
                membership.save()
    except Exception as e:
        return Response({'error: error occured in signal'})