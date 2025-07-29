# from datetime import date
# from reward_point.models import Action_Point, User_Action_History, User_Point
from compute_marketplace.models import Portfolio


def reward_point_register(user, topup_amount):
    # action_point = None
    # user_action_history = None
    # init portfolio money
    # disable for product

    Portfolio.objects.create(
        token_name="United States Dollar",
        token_symbol="USD",
        account=user,
        amount_holding=topup_amount,
    )

    # if not Action_Point.objects.filter(activity = "register").exists():
    #     action_point = Action_Point.objects.create(name = "Early Birds",
    #                                                    date_start=date(2024, 3, 30),
    #                                                    date_end=date(2024, 9, 30),
    #                                                    description = "Benefits include a free first-month trial, Retroactive tokens (will be automatically distributed to your wallet after your account has been created and verified), and the flexibility to use tokens within the platform or convert them to fiat.",
    #                                                    activity = "register",
    #                                                    point = 4,
    #                                                    detail = "Early adopters (the first 6 mons) are rewarded for their early engagement with our platform.\nRegister, verify your account and use our ecosystem which includes data engines & MLOps tools for your AI model development, or rent or lease GPUs/CPUs or trade models or just register to our crowdsourcing pool to join and earn from suitable AI data projects.\nYou will not only enjoy a free trial but will also be eligible for retroactive tokens.",
    #                                                    customer = "AI developers, Model seller, buyers, Compute providers Crowdsourcing freelancers",
    #                                                    note = "Active users will get more scores than inactive users who just create an account then leave it inactive.\nYour acc needs to be fully verified.\nMake sure you choose the right role (AI builder/Compute provider/ Freelancer/ etc)"
    #         )
    # else:
    #     action_point = Action_Point.objects.filter(activity = "register").first()
    #
    # if action_point:
    #     user_action_history = User_Action_History.objects.create(user = user, action = action_point, point = 4, status = 0)
    #
    # if user_action_history:
    #     User_Point.objects.create(
    #             user=user,
    #             point=user_action_history.point
    #         )
