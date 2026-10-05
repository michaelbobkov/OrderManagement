package com.example.orders;

import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/** Posts order events to the notification service. Failures never fail order creation. */
@Component
public class NotificationClient {
    private static final Logger LOG = LoggerFactory.getLogger(NotificationClient.class);
    private final RestClient client;

    public NotificationClient(@Value("${notification.url}") String baseUrl) {
        this.client = RestClient.builder().baseUrl(baseUrl).build();
    }

    public boolean send(Order order) {
        try {
            client.post().uri("/events")
                    .body(Map.of("type", "order.created", "order_id", order.id(),
                            "customer", order.customer(), "amount", order.total()))
                    .retrieve().toBodilessEntity();
            return true;
        } catch (Exception e) {
            LOG.warn("notification failed for order {}: {}", order.id(), e.getMessage());
            return false;
        }
    }
}
