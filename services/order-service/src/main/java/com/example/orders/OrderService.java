package com.example.orders;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.MeterRegistry;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Service;

@Service
public class OrderService {
    private final Map<String, Order> orders = new ConcurrentHashMap<>();
    private final Counter created;
    private final DistributionSummary value;
    private final NotificationClient notifications;

    public OrderService(MeterRegistry registry, NotificationClient notifications) {
        this.notifications = notifications;
        this.created = Counter.builder("orders_created").description("Orders created").register(registry);
        this.value = DistributionSummary.builder("order_value").description("Order value in currency units")
                .register(registry);
    }

    public Order create(OrderRequest req) {
        BigDecimal total = req.unitPrice().multiply(BigDecimal.valueOf(req.quantity()));
        Order order = new Order(UUID.randomUUID().toString(), req.customer(), req.item(), req.quantity(),
                total, Instant.now());
        orders.put(order.id(), order);
        created.increment();
        value.record(total.doubleValue());
        notifications.send(order);
        return order;
    }

    public Optional<Order> find(String id) {
        return Optional.ofNullable(orders.get(id));
    }

    public List<Order> all() {
        return new ArrayList<>(orders.values());
    }
}
