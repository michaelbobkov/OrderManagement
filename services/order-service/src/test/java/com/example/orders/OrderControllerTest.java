package com.example.orders;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.jayway.jsonpath.JsonPath;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.actuate.observability.AutoConfigureObservability;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@SpringBootTest
@AutoConfigureMockMvc
@AutoConfigureObservability
class OrderControllerTest {
    private static final String BODY =
            "{\"customer\":\"alice\",\"item\":\"book\",\"quantity\":2,\"unitPrice\":10.50}";

    @Autowired
    MockMvc mvc;
    @MockBean
    NotificationClient notifications;

    @Test
    void createsAndFetchesOrder() throws Exception {
        MvcResult res = mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON).content(BODY))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.total").value(21.00))
                .andReturn();
        String id = JsonPath.read(res.getResponse().getContentAsString(), "$.id");
        mvc.perform(get("/orders/" + id)).andExpect(status().isOk())
                .andExpect(jsonPath("$.customer").value("alice"));
        verify(notifications).send(any(Order.class));
    }

    @Test
    void rejectsInvalidOrder() throws Exception {
        mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON)
                .content("{\"customer\":\"\",\"item\":\"x\",\"quantity\":0,\"unitPrice\":1}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void unknownOrderIs404() throws Exception {
        mvc.perform(get("/orders/nope")).andExpect(status().isNotFound());
    }

    @Test
    void exposesBusinessMetrics() throws Exception {
        mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON).content(BODY))
                .andExpect(status().isCreated());
        mvc.perform(get("/actuator/prometheus")).andExpect(status().isOk())
                .andExpect(content().string(Matchers.containsString("orders_created_total")))
                .andExpect(content().string(Matchers.containsString("order_value")));
    }
}
