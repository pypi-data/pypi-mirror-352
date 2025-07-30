# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ....types.v2 import Chain
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.chain import Chain
from ....types.v2.accounts import (
    OrderTif,
    OrderSide,
    OrderType,
    order_list_params,
    order_get_fee_quote_params,
    order_get_fulfillments_params,
)
from ....types.v2.accounts.order import Order
from ....types.v2.accounts.order_tif import OrderTif
from ....types.v2.accounts.order_side import OrderSide
from ....types.v2.accounts.order_type import OrderType
from ....types.v2.accounts.order_list_response import OrderListResponse
from ....types.v2.accounts.order_get_fee_quote_response import OrderGetFeeQuoteResponse
from ....types.v2.accounts.order_get_fulfillments_response import OrderGetFulfillmentsResponse

__all__ = ["OrdersResource", "AsyncOrdersResource"]


class OrdersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OrdersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OrdersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrdersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return OrdersResourceWithStreamingResponse(self)

    def retrieve(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """
        Get a specific `Order` by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    def list(
        self,
        account_id: str,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderListResponse:
        """
        Get a list of all `Orders` under the `Account`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/orders",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    order_list_params.OrderListParams,
                ),
            ),
            cast_to=OrderListResponse,
        )

    def cancel(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """Cancel an `Order` by its ID.

        Note that this requires the `Order` ID, not the
        `OrderRequest` ID. Once you submit a cancellation request, it cannot be undone.
        Be advised that orders with a status of PENDING_FILL, PENDING_ESCROW, FILLED,
        REJECTED, or CANCELLED cannot be cancelled.

        `Order` cancellation is not guaranteed nor is it immediate. The `Order` may
        still be executed if the cancellation request is not received in time.

        Check the status using the "Get Order by ID" endpoint to confirm whether the
        `Order` has been cancelled.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    def get_fee_quote(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        contract_address: str,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token: str | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderGetFeeQuoteResponse:
        """
        Get fee quote data for an `Order`.

        The `order_fee_contract_object` property contains the fee quote structure to be
        used verbatim when placing an `Order` directly through our Contracts.

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          contract_address: Address of the smart contract that will create the `Order`.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          stock_id: The Stock ID associated with the Order

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token: Address of payment token.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/orders/fee_quote",
            body=maybe_transform(
                {
                    "chain_id": chain_id,
                    "contract_address": contract_address,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "limit_price": limit_price,
                    "payment_token": payment_token,
                    "payment_token_quantity": payment_token_quantity,
                },
                order_get_fee_quote_params.OrderGetFeeQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderGetFeeQuoteResponse,
        )

    def get_fulfillments(
        self,
        order_id: str,
        *,
        account_id: str,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderGetFulfillmentsResponse:
        """
        Get `OrderFulfillments` for a specific `Order`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/fulfillments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    order_get_fulfillments_params.OrderGetFulfillmentsParams,
                ),
            ),
            cast_to=OrderGetFulfillmentsResponse,
        )


class AsyncOrdersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOrdersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrdersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrdersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return AsyncOrdersResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """
        Get a specific `Order` by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    async def list(
        self,
        account_id: str,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderListResponse:
        """
        Get a list of all `Orders` under the `Account`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/orders",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    order_list_params.OrderListParams,
                ),
            ),
            cast_to=OrderListResponse,
        )

    async def cancel(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """Cancel an `Order` by its ID.

        Note that this requires the `Order` ID, not the
        `OrderRequest` ID. Once you submit a cancellation request, it cannot be undone.
        Be advised that orders with a status of PENDING_FILL, PENDING_ESCROW, FILLED,
        REJECTED, or CANCELLED cannot be cancelled.

        `Order` cancellation is not guaranteed nor is it immediate. The `Order` may
        still be executed if the cancellation request is not received in time.

        Check the status using the "Get Order by ID" endpoint to confirm whether the
        `Order` has been cancelled.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    async def get_fee_quote(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        contract_address: str,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token: str | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderGetFeeQuoteResponse:
        """
        Get fee quote data for an `Order`.

        The `order_fee_contract_object` property contains the fee quote structure to be
        used verbatim when placing an `Order` directly through our Contracts.

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          contract_address: Address of the smart contract that will create the `Order`.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          stock_id: The Stock ID associated with the Order

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token: Address of payment token.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/orders/fee_quote",
            body=await async_maybe_transform(
                {
                    "chain_id": chain_id,
                    "contract_address": contract_address,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "limit_price": limit_price,
                    "payment_token": payment_token,
                    "payment_token_quantity": payment_token_quantity,
                },
                order_get_fee_quote_params.OrderGetFeeQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderGetFeeQuoteResponse,
        )

    async def get_fulfillments(
        self,
        order_id: str,
        *,
        account_id: str,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderGetFulfillmentsResponse:
        """
        Get `OrderFulfillments` for a specific `Order`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/fulfillments",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    order_get_fulfillments_params.OrderGetFulfillmentsParams,
                ),
            ),
            cast_to=OrderGetFulfillmentsResponse,
        )


class OrdersResourceWithRawResponse:
    def __init__(self, orders: OrdersResource) -> None:
        self._orders = orders

        self.retrieve = to_raw_response_wrapper(
            orders.retrieve,
        )
        self.list = to_raw_response_wrapper(
            orders.list,
        )
        self.cancel = to_raw_response_wrapper(
            orders.cancel,
        )
        self.get_fee_quote = to_raw_response_wrapper(
            orders.get_fee_quote,
        )
        self.get_fulfillments = to_raw_response_wrapper(
            orders.get_fulfillments,
        )


class AsyncOrdersResourceWithRawResponse:
    def __init__(self, orders: AsyncOrdersResource) -> None:
        self._orders = orders

        self.retrieve = async_to_raw_response_wrapper(
            orders.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            orders.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            orders.cancel,
        )
        self.get_fee_quote = async_to_raw_response_wrapper(
            orders.get_fee_quote,
        )
        self.get_fulfillments = async_to_raw_response_wrapper(
            orders.get_fulfillments,
        )


class OrdersResourceWithStreamingResponse:
    def __init__(self, orders: OrdersResource) -> None:
        self._orders = orders

        self.retrieve = to_streamed_response_wrapper(
            orders.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            orders.list,
        )
        self.cancel = to_streamed_response_wrapper(
            orders.cancel,
        )
        self.get_fee_quote = to_streamed_response_wrapper(
            orders.get_fee_quote,
        )
        self.get_fulfillments = to_streamed_response_wrapper(
            orders.get_fulfillments,
        )


class AsyncOrdersResourceWithStreamingResponse:
    def __init__(self, orders: AsyncOrdersResource) -> None:
        self._orders = orders

        self.retrieve = async_to_streamed_response_wrapper(
            orders.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            orders.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            orders.cancel,
        )
        self.get_fee_quote = async_to_streamed_response_wrapper(
            orders.get_fee_quote,
        )
        self.get_fulfillments = async_to_streamed_response_wrapper(
            orders.get_fulfillments,
        )
