# Account

Subscription entitlements, purchase history, and referral program.

## Contents

- [Subscriptions](#subscriptions)
- [Redeem Subscription](#redeem-subscription)
- [Purchase History](#purchase-history)
- [Referral Program](#referral-program)

## Subscriptions

```
GET https://app-api.8slp.net/v3/users/{userId}/subscriptions
```

Response:
```json
{
  "subscriptions": [
    {
      "ownerUserId": "partnerId",
      "subscriberRelationship": "partner",
      "subscriptionId": "grandfathered",
      "type": "premium",
      "status": "active",
      "createdAt": "2021-12-05T07:19:55Z",
      "willRenew": false,
      "hasBillingFailure": false,
      "isUnpaidPremium": true,
      "inGracePeriod": false,
      "subscriptionFrequency": "lifetime",
      "subscriptionProductName": "grandfathered",
      "provider": "eight_internal",
      "isRental": false,
      "isActive": true,
      "isActivePremium": true,
      "isActiveBasic": false
    },
    {
      "ownerUserId": "partnerId",
      "subscriberRelationship": "partner",
      "subscriptionId": "basic-dpimdkoc",
      "type": "basic",
      "status": "active",
      "createdAt": "1970-01-01T00:00:00Z",
      "willRenew": false,
      "hasBillingFailure": false,
      "isUnpaidPremium": false,
      "inGracePeriod": false,
      "subscriptionFrequency": "lifetime",
      "subscriptionProductName": "basic",
      "provider": "eight_internal",
      "isRental": false,
      "isActive": true,
      "isActivePremium": false,
      "isActiveBasic": true
    },
    {
      "ownerUserId": "selfId",
      "subscriberRelationship": "self",
      "subscriptionId": "basic-1yxq63fj",
      "type": "basic",
      "status": "active",
      "createdAt": "1970-01-01T00:00:00Z",
      "willRenew": false,
      "hasBillingFailure": false,
      "isUnpaidPremium": false,
      "inGracePeriod": false,
      "subscriptionFrequency": "lifetime",
      "subscriptionProductName": "basic",
      "provider": "eight_internal",
      "isRental": false,
      "isActive": true,
      "isActivePremium": false,
      "isActiveBasic": true
    }
  ],
  "primarySubscription": {
    "...same shape as a subscription entry..."
  },
  "hasBasic": true,
  "hasAccessToBasicFeatures": true,
  "hasAccessToPremiumFeatures": true,
  "isUnpaidPremium": true,
  "isInGracePeriod": false,
  "capabilities": [
    "autopilot",
    "away_mode",
    "device_setup",
    "insights",
    "limited_maintenance_inserts",
    "member_shop_and_referral",
    "multi_pod_support",
    "partner_management_and_temperature_control",
    "sleep_and_health_reporting",
    "sleep_content",
    "smart_elevation",
    "snoring_detection",
    "snoring_mitigation",
    "temperature_control_widget",
    "temperature_control_with_timer",
    "temperature_scheduling",
    "vibration_and_temperature_wake_up"
  ],
  "churned": false
}
```

Notes:
- This is a **v3** endpoint — the only v3 path observed in the API.
- Fetched on every app launch (part of the initial burst).
- `subscriberRelationship`: observed values `"self"`, `"partner"`. A partner subscription means the `ownerUserId` is a different user.
- `type`: observed values `"premium"`, `"basic"`.
- `subscriptionFrequency`: observed value `"lifetime"`. Other values unknown.
- `provider`: observed value `"eight_internal"`. Other values unknown.
- `primarySubscription`: appears to duplicate the highest-tier active subscription from the array.
- `capabilities`: list of feature gates. Unclear how this relates to the `features` array on the user/device endpoints (which may reflect hardware capabilities rather than subscription entitlements — not confirmed).
- `churned`, `isRental`, `inGracePeriod`, `hasBillingFailure`, `willRenew`: purpose suggested by field names but not confirmed via observation (all were `false` in our capture).

## Redeem Subscription

```
POST https://app-api.8slp.net/v3/users/{userId}/subscriptions/redeem
```

Body:
```json
{
  "userId": "userId",
  "email": "user@example.com"
}
```

Response (no subscription to redeem):
```json
{
  "subscriptions": [],
  "captureStatus": { "type": "no-subscriptions" },
  "hasBasic": false,
  "hasAccessToBasicFeatures": false,
  "hasAccessToPremiumFeatures": false,
  "isUnpaidPremium": false,
  "isInGracePeriod": false,
  "capabilities": [
    "device_setup",
    "multi_pod_support",
    "partner_management_and_temperature_control",
    "temperature_control_with_timer"
  ],
  "churned": false
}
```

Notes:
- Observed during new account creation. Presumably also used when redeeming a subscription code, though that flow has not been captured.
- `captureStatus.type`: observed value `"no-subscriptions"`. Other values unknown.
- A user with no subscription still gets basic capabilities (`device_setup`, `multi_pod_support`, `partner_management_and_temperature_control`, `temperature_control_with_timer`) — fewer than a subscribed user.

## Purchase History

```
GET https://app-api.8slp.net/v1/purchase-tracker?email={email}
```

Note: takes email as a query param, not user ID.

Response:
```json
{
  "purchases": [
    {
      "purchasedAt": "2024-05-25T08:39:09Z",
      "products": [
        {
          "type": "pod",
          "podType": "pod4",
          "coverVersion": "a25c",
          "size": "US-queen",
          "shipping": {
            "status": "confirmed"
          }
        },
        {
          "type": "adjustable-base",
          "size": "US-queen",
          "shipping": {
            "status": "confirmed"
          }
        },
        "..."
      ],
      "isPurchaser": true
    },
    "..."
  ]
}
```

Notes:
- `type`: observed values `"pod"`, `"adjustable-base"`. Likely also `"pillow"`, `"blanket"`, etc.
- `podType`: observed value `"pod4"`.
- `shipping.status`: observed value `"confirmed"`. Other values unknown.
- `isPurchaser`: `true` for the account that placed the order. Possibly `false` for a partner who received access through sharing.
- Fetched on app launch.

## Referral Program

```
GET https://app-api.8slp.net/v2/users/{userId}/referral/campaigns
```

Response:
```json
{
  "campaignId": "uuid",
  "currency": "$",
  "sideMenuCopy": "Send $350",
  "headlineCopy": "Give the gift of a lifetime",
  "subheadlineCopy": "Share your referral link to give friends up to $350 off their Pod purchase. You'll get a $100 gift card for each friend who purchases. It's a win-win.",
  "topButtonCopy": "Invite Friends",
  "assetLink": "https://eight-eightsleep-react.s3.us-east-2.amazonaws.com/assets/referral_in_app_pod5_v2.jpg"
}
```

Notes:
- Marketing copy and referral link configuration.
- Fetched on app launch.
- Response is a single campaign object, not an array (despite the `/campaigns` path).
