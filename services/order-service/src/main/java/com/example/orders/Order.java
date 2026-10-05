package com.example.orders;

import java.math.BigDecimal;
import java.time.Instant;

public record Order(String id, String customer, String item, int quantity, BigDecimal total, Instant createdAt) {
}
