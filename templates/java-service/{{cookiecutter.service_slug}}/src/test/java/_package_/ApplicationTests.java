package {{ cookiecutter.package_name }};

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

/** Platform smoke tests: if these fail, the golden path itself is broken. */
@SpringBootTest
@AutoConfigureMockMvc
class ApplicationTests {

  @Autowired private MockMvc mvc;

  @Test
  void healthEndpointIsUp() throws Exception {
    mvc.perform(get("/actuator/health"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.status").value("UP"));
  }

  @Test
  void everyResponseCarriesARequestId() throws Exception {
    mvc.perform(get("/actuator/health")).andExpect(header().exists("X-Request-Id"));
  }

  @Test
  void prometheusMetricsAreExposed() throws Exception {
    mvc.perform(get("/actuator/prometheus")).andExpect(status().isOk());
  }
}
