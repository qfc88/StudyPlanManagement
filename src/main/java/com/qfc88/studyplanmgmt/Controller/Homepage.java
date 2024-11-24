package com.qfc88.studyplanmgmt.Controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Homepage {

    @GetMapping("/")
    public String homepage(){
        return "Welcome to the homepage";
    }
}
