package com.qfc88.studyplanmgmt.Controller;

import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.security.core.annotation.AuthenticationPrincipal;

@RestController
public class Homepage {

   @GetMapping("/home")
    public String home(@AuthenticationPrincipal OAuth2User principal, Model model) {
        // Add user name to the model
        model.addAttribute("id", principal.getAttribute("id"));
        model.addAttribute("name", principal.getAttribute("name"));
        model.addAttribute("email", principal.getAttribute("email"));
        return model.toString();
    }
}
