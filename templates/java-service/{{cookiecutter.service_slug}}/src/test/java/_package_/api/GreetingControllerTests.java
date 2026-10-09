package {{ cookiecutter.package_name }}.api;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class GreetingControllerTests {

  @Autowired private MockMvc mvc;

  @Test
  void greetsByName() throws Exception {
    mvc.perform(get("/api/greeting").param("name", "Platform"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.message").value("Hello, Platform!"));
  }

  @Test
  void rejectsBadInputWithProblemDetails() throws Exception {
    mvc.perform(get("/api/greeting").param("name", " "))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.status").value(400));
  }
}
