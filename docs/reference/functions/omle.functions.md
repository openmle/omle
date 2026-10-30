# omle.functions — Functions

_Standard elementwise expression functions for OMLE v0.1._

**Registry version:** 0.1

## Functions

| Function | Category | Summary |
|----------|----------|---------|
| [`cast`](#cast) | conversion | Elementwise type conversion. |
| [`add`](#add) | arithmetic | Elementwise numeric addition. |
| [`sub`](#sub) | arithmetic | Elementwise numeric subtraction. |
| [`mul`](#mul) | arithmetic | Elementwise numeric multiplication. |
| [`div`](#div) | arithmetic | Elementwise numeric division. |
| [`floordiv`](#floordiv) | arithmetic | Elementwise floor-style integer division. |
| [`mod`](#mod) | arithmetic | Elementwise remainder. |
| [`neg`](#neg) | arithmetic | Elementwise numeric negation. |
| [`abs`](#abs) | arithmetic | Elementwise absolute value. |
| [`sum`](#sum) | arithmetic | Elementwise sum across multiple numeric arguments. |
| [`avg`](#avg) | arithmetic | Elementwise average across multiple numeric arguments. |
| [`product`](#product) | arithmetic | Elementwise product across multiple numeric arguments. |
| [`pow`](#pow) | math | Elementwise exponentiation. |
| [`sqrt`](#sqrt) | math | Elementwise square root. |
| [`exp`](#exp) | math | Elementwise exponential. |
| [`log`](#log) | math | Elementwise natural logarithm. |
| [`log2`](#log2) | math | Elementwise base-2 logarithm. |
| [`log10`](#log10) | math | Elementwise base-10 logarithm. |
| [`ln1p`](#ln1p) | math | Elementwise natural logarithm of 1 + x. |
| [`round`](#round) | math | Elementwise rounding. |
| [`floor`](#floor) | math | Elementwise floor. |
| [`ceil`](#ceil) | math | Elementwise ceil. |
| [`sign`](#sign) | math | Elementwise sign function. |
| [`threshold`](#threshold) | math | Elementwise threshold comparison. |
| [`equal`](#equal) | comparison | Elementwise equality comparison. |
| [`not_equal`](#not_equal) | comparison | Elementwise inequality comparison. |
| [`less_than`](#less_than) | comparison | Elementwise less-than comparison. |
| [`less_or_equal`](#less_or_equal) | comparison | Elementwise less-than-or-equal comparison. |
| [`greater_than`](#greater_than) | comparison | Elementwise greater-than comparison. |
| [`greater_or_equal`](#greater_or_equal) | comparison | Elementwise greater-than-or-equal comparison. |
| [`and`](#and) | boolean | Elementwise boolean conjunction. |
| [`or`](#or) | boolean | Elementwise boolean disjunction. |
| [`xor`](#xor) | boolean | Elementwise boolean exclusive-or. |
| [`not`](#not) | boolean | Elementwise boolean negation. |
| [`if`](#if) | conditional | Elementwise conditional selection. |
| [`coalesce`](#coalesce) | null | Return the first non-null argument. |
| [`is_missing`](#is_missing) | null | Test whether the input is null. |
| [`isnull`](#isnull) | null | Alias for is_missing. |
| [`is_not_missing`](#is_not_missing) | null | Test whether the input is not null. |
| [`map_values`](#map_values) | mapping | Map input values through explicit key-value pairs. |
| [`min`](#min) | math | Elementwise minimum of two numeric arguments. |
| [`max`](#max) | math | Elementwise maximum of two numeric arguments. |
| [`clip`](#clip) | math | Clamp values to [lo, hi]. |
| [`concat`](#concat) | string | Elementwise string concatenation. |
| [`length`](#length) | string | Elementwise string length. |
| [`lower`](#lower) | string | Elementwise lowercase conversion. |
| [`upper`](#upper) | string | Elementwise uppercase conversion. |
| [`trim`](#trim) | string | Elementwise string trim. |
| [`substring`](#substring) | string | Elementwise substring extraction. |
| [`in`](#in) | membership | Test whether a value is in a provided set. |
| [`not_in`](#not_in) | membership | Test whether a value is not in a provided set. |
| [`dateDaysSinceYear`](#datedayssinceyear) | datetime | Return the signed day offset from January 1 of a reference year. |
| [`dateSecondsSinceYear`](#datesecondssinceyear) | datetime | Return the signed second offset from January 1 of a reference year. |
| [`dateSecondsSinceMidnight`](#datesecondssincemidnight) | datetime | Return the second offset from midnight. |
| [`erf`](#erf) | distribution | Elementwise error function. |
| [`stdNormalPDF`](#stdnormalpdf) | distribution | Elementwise standard normal probability density. |
| [`stdNormalCDF`](#stdnormalcdf) | distribution | Elementwise standard normal cumulative probability. |
| [`stdNormalIDF`](#stdnormalidf) | distribution | Elementwise standard normal inverse cumulative probability. |
| [`normalPDF`](#normalpdf) | distribution | Elementwise normal probability density. |
| [`normalCDF`](#normalcdf) | distribution | Elementwise normal cumulative probability. |
| [`normalIDF`](#normalidf) | distribution | Elementwise normal inverse cumulative probability. |

---

## cast

**Category:** conversion  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise type conversion.

Converts x elementwise to the requested target type.

```
cast(*x*, *target_type*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | any | no |
| `target_type` | string | no |

### Returns

- **Type:** target_type
- **Measure level:** same_as(x)

### Notes

- target_type must name a valid OMLE scalar DataType.
- Failed conversions yield null or runtime error according to profile; standard v0.1 should prefer null.

---

## add

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise numeric addition.

Returns the elementwise sum of x and y.

```
add(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous_if_numeric(args)

---

## sub

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise numeric subtraction.

Returns the elementwise difference x - y.

```
sub(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous_if_numeric(args)

---

## mul

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise numeric multiplication.

Returns the elementwise product of x and y.

```
mul(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous_if_numeric(args)

---

## div

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise numeric division.

Returns the elementwise quotient x / y.

```
div(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** float_division(x,y)
- **Measure level:** continuous_if_numeric(args)

### Notes

- Division always produces a floating-point result, even for integer operands.
- Division-by-zero behavior is runtime-defined unless constrained by profile.

---

## floordiv

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise floor-style integer division.

Returns the elementwise integer quotient of x divided by y using mathematical floor semantics.

```
floordiv(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | integer | no |
| `y` | integer | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous_if_numeric(args)

### Notes

- For negative operands, behavior follows mathematical floor division, not truncation toward zero.
- Division-by-zero behavior is runtime-defined unless constrained by profile.

---

## mod

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise remainder.

Returns the elementwise remainder associated with floor-style integer division.

```
mod(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | integer | no |
| `y` | integer | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous_if_numeric(args)

### Notes

- v0.1 restricts mod to integer operands. Floating-point modulo may be added in a future version.
- For negative operands, mod is defined consistently with floordiv.

---

## neg

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise numeric negation.

Returns the elementwise negation of x.

```
neg(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** same_as(x)
- **Measure level:** continuous_if_numeric(args)

---

## abs

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise absolute value.

Returns the elementwise absolute value of x.

```
abs(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** same_as(x)
- **Measure level:** continuous_if_numeric(args)

---

## sum

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise sum across multiple numeric arguments.

Returns the elementwise sum of all provided numeric arguments.

```
sum(*x1*, *x2...)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x1` | numeric | no |
| `x2` | numeric | yes |

### Returns

- **Type:** numeric_promotion(args)
- **Measure level:** continuous_if_numeric(args)

---

## avg

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise average across multiple numeric arguments.

Returns the elementwise arithmetic mean of all provided numeric arguments.

```
avg(*x1*, *x2...)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x1` | numeric | no |
| `x2` | numeric | yes |

### Returns

- **Type:** float_if_numeric(args)
- **Measure level:** continuous

---

## product

**Category:** arithmetic  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise product across multiple numeric arguments.

Returns the elementwise product of all provided numeric arguments.

```
product(*x1*, *x2...)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x1` | numeric | no |
| `x2` | numeric | yes |

### Returns

- **Type:** numeric_promotion(args)
- **Measure level:** continuous_if_numeric(args)

---

## pow

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise exponentiation.

Returns x raised elementwise to the power y.

```
pow(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** float_if_numeric(args)
- **Measure level:** continuous

---

## sqrt

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise square root.

Returns the elementwise square root of x.

```
sqrt(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## exp

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise exponential.

Returns the elementwise exponential of x.

```
exp(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## log

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise natural logarithm.

Returns the elementwise natural logarithm of x.

```
log(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## log2

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise base-2 logarithm.

Returns the elementwise base-2 logarithm of x.

```
log2(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## log10

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise base-10 logarithm.

Returns the elementwise base-10 logarithm of x.

```
log10(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## ln1p

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise natural logarithm of 1 + x.

Returns the elementwise natural logarithm of 1 + x.

```
ln1p(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## round

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise rounding.

Returns x rounded elementwise.

```
round(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** same_as(x)
- **Measure level:** continuous

### Notes

- Rounding uses round-half-to-even.

---

## floor

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise floor.

Returns the elementwise floor of x.

```
floor(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** same_as(x)
- **Measure level:** continuous

---

## ceil

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise ceil.

Returns the elementwise ceiling of x.

```
ceil(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** same_as(x)
- **Measure level:** continuous

---

## sign

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise sign function.

Returns -1 for negative values, 0 for zero, and 1 for positive values.

```
sign(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** int64
- **Measure level:** ordinal

---

## threshold

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise threshold comparison.

Returns true where x is greater than the provided threshold value.

```
threshold(*x*, *threshold*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `threshold` | numeric | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## equal

**Category:** comparison  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise equality comparison.

Returns true where x and y are equal.

```
equal(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `y` | comparable | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- Equality is exact at the represented dtype level.
- The validator must require x and y to be mutually comparable or coercible under the active typing rules.

---

## not_equal

**Category:** comparison  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise inequality comparison.

Returns true where x and y are not equal.

```
not_equal(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `y` | comparable | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require x and y to be mutually comparable or coercible under the active typing rules.

---

## less_than

**Category:** comparison  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise less-than comparison.

Returns true where x < y.

```
less_than(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `y` | comparable | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require x and y to be mutually orderable or coercible under the active typing rules.

---

## less_or_equal

**Category:** comparison  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise less-than-or-equal comparison.

Returns true where x <= y.

```
less_or_equal(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `y` | comparable | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require x and y to be mutually orderable or coercible under the active typing rules.

---

## greater_than

**Category:** comparison  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise greater-than comparison.

Returns true where x > y.

```
greater_than(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `y` | comparable | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require x and y to be mutually orderable or coercible under the active typing rules.

---

## greater_or_equal

**Category:** comparison  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise greater-than-or-equal comparison.

Returns true where x >= y.

```
greater_or_equal(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `y` | comparable | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require x and y to be mutually orderable or coercible under the active typing rules.

---

## and

**Category:** boolean  ·  **Since:** 0.1  ·  **Null rule:** three_valued

Elementwise boolean conjunction.

Returns x AND y elementwise using three-valued logic.

```
and(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | boolean | no |
| `y` | boolean | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## or

**Category:** boolean  ·  **Since:** 0.1  ·  **Null rule:** three_valued

Elementwise boolean disjunction.

Returns x OR y elementwise using three-valued logic.

```
or(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | boolean | no |
| `y` | boolean | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## xor

**Category:** boolean  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise boolean exclusive-or.

Returns x XOR y elementwise.

```
xor(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | boolean | no |
| `y` | boolean | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- For XOR, null propagates strictly because neither operand alone determines the result.

---

## not

**Category:** boolean  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise boolean negation.

Returns NOT x elementwise.

```
not(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | boolean | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## if

**Category:** conditional  ·  **Since:** 0.1  ·  **Null rule:** if_condition

Elementwise conditional selection.

Returns then_value where condition is true, else else_value.

```
if(*condition*, *then_value*, *else_value*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `condition` | boolean | no |
| `then_value` | any | no |
| `else_value` | any | no |

### Returns

- **Type:** common_supertype(args)
- **Measure level:** common_branch_measure_level(args)

### Notes

- Branches are evaluated lazily: only the selected branch is evaluated.
- The validator must require then_value and else_value to have compatible types and measure levels.

---

## coalesce

**Category:** null  ·  **Since:** 0.1  ·  **Null rule:** coalesce

Return the first non-null argument.

Evaluates arguments left to right and returns the first non-null value.

```
coalesce(*x1*, *x2...)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x1` | any | no |
| `x2` | any | yes |

### Returns

- **Type:** common_supertype(args)
- **Measure level:** same_as_non_null(args)

---

## is_missing

**Category:** null  ·  **Since:** 0.1  ·  **Null rule:** is_missing

Test whether the input is null.

Returns true where x is missing/null.

```
is_missing(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | any | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## isnull

**Category:** null  ·  **Since:** 0.1  ·  **Null rule:** is_missing

Alias for is_missing.

Returns true where x is missing/null. This is an alias for is_missing.

```
isnull(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | any | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## is_not_missing

**Category:** null  ·  **Since:** 0.1  ·  **Null rule:** is_not_missing

Test whether the input is not null.

Returns true where x is not missing/null.

```
is_not_missing(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | any | no |

### Returns

- **Type:** boolean
- **Measure level:** flag

---

## map_values

**Category:** mapping  ·  **Since:** 0.1  ·  **Null rule:** strict

Map input values through explicit key-value pairs.

If x is missing, returns map_missing_to when provided, else null. Otherwise returns the mapped value for the first matching from/to pair. If no mapping matches, returns default_value when provided, else null.

```
map_values(*x*, *pairs..., [default_value=...], [map_missing_to=...])
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `pairs` | any | yes |

### Optional Parameters

| Name | Kind(s) |
|------|---------|
| `default_value` | any |
| `map_missing_to` | any |

### Returns

- **Type:** same_as_non_null_result_values(args)
- **Measure level:** same_as_non_null_result_values(args)

### Notes

- pairs are interpreted as from/to pairs.
- The validator must require an even number of pair elements.
- The validator must type-check pair elements as alternating key/value entries.
- The result type is inferred from mapped values plus optional result-side defaults, not from x or key-side pair entries.
- If x is missing and map_missing_to is present, map_missing_to is returned.
- If x is non-missing and no pair matches, default_value is returned when present.

---

## min

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise minimum of two numeric arguments.

Returns the elementwise minimum of x and y.

```
min(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous

---

## max

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise maximum of two numeric arguments.

Returns the elementwise maximum of x and y.

```
max(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `y` | numeric | no |

### Returns

- **Type:** numeric_promotion(a,b)
- **Measure level:** continuous

---

## clip

**Category:** math  ·  **Since:** 0.1  ·  **Null rule:** strict

Clamp values to [lo, hi].

Returns x clamped elementwise to the inclusive interval [lo, hi].

```
clip(*x*, *lo*, *hi*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `lo` | numeric | no |
| `hi` | numeric | no |

### Returns

- **Type:** numeric_promotion(args)
- **Measure level:** continuous

### Notes

- This function has the same scalar semantics as the core Clip operator, but is used inside expressions.

---

## concat

**Category:** string  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise string concatenation.

Returns the elementwise concatenation of x and y.

```
concat(*x*, *y*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | string | no |
| `y` | string | no |

### Returns

- **Type:** string
- **Measure level:** nominal

---

## length

**Category:** string  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise string length.

Returns the elementwise length of x.

```
length(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | string | no |

### Returns

- **Type:** int64
- **Measure level:** continuous

### Notes

- Length is measured in Unicode code points, not bytes.

---

## lower

**Category:** string  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise lowercase conversion.

Returns x converted to lowercase elementwise.

```
lower(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | string | no |

### Returns

- **Type:** string
- **Measure level:** same_as(x)

---

## upper

**Category:** string  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise uppercase conversion.

Returns x converted to uppercase elementwise.

```
upper(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | string | no |

### Returns

- **Type:** string
- **Measure level:** same_as(x)

---

## trim

**Category:** string  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise string trim.

Returns x with leading and trailing whitespace removed elementwise.

```
trim(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | string | no |

### Returns

- **Type:** string
- **Measure level:** same_as(x)

---

## substring

**Category:** string  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise substring extraction.

Returns a substring of x using integer start and length arguments.

```
substring(*x*, *start*, *length*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | string | no |
| `start` | integer | no |
| `length` | integer | no |

### Returns

- **Type:** string
- **Measure level:** same_as(x)

### Notes

- start is 0-based and measured in Unicode code points.
- length is measured in Unicode code points.
- If start + length exceeds the string length, the result is truncated silently.
- Negative start or length yields null.

---

## in

**Category:** membership  ·  **Since:** 0.1  ·  **Null rule:** strict

Test whether a value is in a provided set.

Returns true where x matches any provided set member.

```
in(*x*, *s1*, *s2...)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `s1` | comparable | no |
| `s2` | comparable | yes |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require all set members to be mutually comparable with x or coercible under the active typing rules.
- Duplicate set members are allowed but have no additional semantic effect.

---

## not_in

**Category:** membership  ·  **Since:** 0.1  ·  **Null rule:** strict

Test whether a value is not in a provided set.

Returns true where x matches none of the provided set members.

```
not_in(*x*, *s1*, *s2...)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | comparable | no |
| `s1` | comparable | no |
| `s2` | comparable | yes |

### Returns

- **Type:** boolean
- **Measure level:** flag

### Notes

- The validator must require all set members to be mutually comparable with x or coercible under the active typing rules.
- Duplicate set members are allowed but have no additional semantic effect.

---

## dateDaysSinceYear

**Category:** datetime  ·  **Since:** 0.1  ·  **Null rule:** strict

Return the signed day offset from January 1 of a reference year.

Returns the elementwise number of calendar days between x and the start of the given reference year.

```
dateDaysSinceYear(*x*, *year*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | date | no |
| `year` | integer | no |

### Returns

- **Type:** int64
- **Measure level:** continuous

### Notes

- v0.1 restricts x to DATE inputs.
- The reference point is the civil date year-01-01.
- The result is signed and may be negative.

---

## dateSecondsSinceYear

**Category:** datetime  ·  **Since:** 0.1  ·  **Null rule:** strict

Return the signed second offset from January 1 of a reference year.

Returns the elementwise number of elapsed seconds between x and the start of the given reference year.

```
dateSecondsSinceYear(*x*, *year*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | timestamp | no |
| `year` | integer | no |

### Returns

- **Type:** int64
- **Measure level:** continuous

### Notes

- v0.1 restricts x to TIMESTAMP inputs.
- The reference point is year-01-01T00:00:00.
- The result is signed and may be negative.

---

## dateSecondsSinceMidnight

**Category:** datetime  ·  **Since:** 0.1  ·  **Null rule:** strict

Return the second offset from midnight.

Returns the elementwise number of elapsed seconds since 00:00:00.

```
dateSecondsSinceMidnight(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | time | no |

### Returns

- **Type:** int64
- **Measure level:** continuous

### Notes

- v0.1 restricts x to TIME inputs.
- The result is in the range supported by the TIME value domain.

---

## erf

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise error function.

Returns the elementwise Gauss error function of x.

```
erf(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## stdNormalPDF

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise standard normal probability density.

Returns the elementwise probability density of the standard normal distribution at x.

```
stdNormalPDF(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

---

## stdNormalCDF

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise standard normal cumulative probability.

Returns the elementwise cumulative probability of the standard normal distribution at x.

```
stdNormalCDF(*x*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |

### Returns

- **Type:** float_if_numeric(x)
- **Measure level:** continuous

### Notes

- The result is in the interval [0,1].

---

## stdNormalIDF

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise standard normal inverse cumulative probability.

Returns the elementwise inverse cumulative probability of the standard normal distribution for p.

```
stdNormalIDF(*p*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `p` | numeric | no |

### Returns

- **Type:** float_if_numeric(p)
- **Measure level:** continuous

### Notes

- p must be in the open interval (0,1).

---

## normalPDF

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise normal probability density.

Returns the elementwise probability density of the normal distribution with mean and standard deviation at x.

```
normalPDF(*x*, *mean*, *stddev*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `mean` | numeric | no |
| `stddev` | numeric | no |

### Returns

- **Type:** float_if_numeric(args)
- **Measure level:** continuous

### Notes

- stddev must be greater than 0.

---

## normalCDF

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise normal cumulative probability.

Returns the elementwise cumulative probability of the normal distribution with mean and standard deviation at x.

```
normalCDF(*x*, *mean*, *stddev*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `x` | numeric | no |
| `mean` | numeric | no |
| `stddev` | numeric | no |

### Returns

- **Type:** float_if_numeric(args)
- **Measure level:** continuous

### Notes

- stddev must be greater than 0.
- The result is in the interval [0,1].

---

## normalIDF

**Category:** distribution  ·  **Since:** 0.1  ·  **Null rule:** strict

Elementwise normal inverse cumulative probability.

Returns the elementwise inverse cumulative probability of the normal distribution with mean and standard deviation for p.

```
normalIDF(*p*, *mean*, *stddev*)
```

### Arguments

| Name | Kind(s) | Variadic |
|------|---------|----------|
| `p` | numeric | no |
| `mean` | numeric | no |
| `stddev` | numeric | no |

### Returns

- **Type:** float_if_numeric(args)
- **Measure level:** continuous

### Notes

- p must be in the open interval (0,1).
- stddev must be greater than 0.

---
