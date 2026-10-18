
import os

from fastapi import FastAPI, Header, HTTPException

app = FastAPI(
    title="Payment Decline Demo API",
    description="Fictional API for a customer-support interview demo.",
)

API_KEY = os.getenv("DEMO_API_KEY")

# Fictional transactions 
TRANSACTIONS = {
    "txn_1001": {
        "decline_code": "INSUFFICIENT_FUNDS",
        "origin": "issuer",
        "retryable": True,
    },
    "txn_1002": {
        "decline_code": "EXPIRED_CARD",
        "origin": "issuer",
        "retryable": False,
    },
    "txn_1003": {
        "decline_code": "IDENTITY_CHECK_REQUIRED",
        "origin": "internal",
        "retryable": False,
    },
    "txn_1004": {
        "decline_code": "RESTRICTED_RISK",
        "origin": "internal",
        "retryable": False,
    },
    "txn_1005": {
        "decline_code": "TECHNICAL_FAILURE",
        "origin": "processor",
        "retryable": True,
    },
    "txn_1006": {
        "decline_code": "NEW_UNKNOWN_CODE",
        "origin": "unknown",
        "retryable": False,
    },
}

POLICIES = {
    "INSUFFICIENT_FUNDS": {
        "customer_message": (
            "There may not be enough available funds for this payment."
        ),
        "next_action": (
            "Check your available balance before trying again."
        ),
        "retry_guidance": "Retry only after checking the balance.",
        "disclosure_level": "customer_safe",
        "escalation_required": False,
    },
    "EXPIRED_CARD": {
        "customer_message": (
            "The card used for this payment may have expired."
        ),
        "next_action": (
            "Check your card details and update them through "
            "the approved secure process if needed."
        ),
        "retry_guidance": "Do not retry until the card issue is fixed.",
        "disclosure_level": "customer_safe",
        "escalation_required": False,
    },
    "IDENTITY_CHECK_REQUIRED": {
        "customer_message": (
            "An additional verification step is needed "
            "before this payment can proceed."
        ),
        "next_action": "Follow the official verification process.",
        "retry_guidance": "Complete verification before retrying.",
        "disclosure_level": "customer_safe",
        "escalation_required": False,
    },
    "RESTRICTED_RISK": {
        "customer_message": (
            "We're unable to approve this payment at the moment."
        ),
        "next_action": (
            "Contact support for help with the available next steps."
        ),
        "retry_guidance": "Do not retry; follow support guidance.",
        "disclosure_level": "restricted",
        "escalation_required": True,
    },
    "TECHNICAL_FAILURE": {
        "customer_message": (
            "There may have been a technical issue processing this payment."
        ),
        "next_action": (
            "Check the payment status or contact support "
            "before attempting another payment."
        ),
        "retry_guidance": (
            "Confirm the final transaction status before retrying."
        ),
        "disclosure_level": "customer_safe",
        "escalation_required": True,
    },
}


@app.get("/")
def home():
    return {
        "service": "Payment Decline Demo API",
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/declines/{transaction_id}")
def get_decline(
    transaction_id: str,
    x_api_key: str = Header(default=""),
):
    # Fail closed if the deployment secret has not been configured.
    if not API_KEY:
        raise HTTPException(
            status_code=503,
            detail="API key is not configured.",
        )

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorised")

    transaction = TRANSACTIONS.get(transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    code = transaction["decline_code"]
    policy = POLICIES.get(code)

    # Unknown codes must never be guessed or treated as safe to retry.
    if policy is None:
        return {
            "transaction_id": transaction_id,
            "decline_code": code,
            "customer_message": (
                "I can't confirm the reason for this decline right now."
            ),
            "next_action": (
                "Please contact support for further help."
            ),
            "retry_guidance": (
                "Do not retry based on this result."
            ),
            "disclosure_level": "unmapped",
            "escalation_required": True,
            "catalogue_version": "1.0",
        }

    return {
        "transaction_id": transaction_id,
        "decline_code": code,
        **transaction,
        **policy,
        "catalogue_version": "1.0",
    }
