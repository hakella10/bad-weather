package com.example.ai;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;

@SpringBootApplication
@EnableAutoConfiguration
@EntityScan(basePackages = {"com.example.ai.controller", "com.example.ai.service", "com.example.ai.model"})
public class BadWeatherApplication {

	public static void main(String[] args) {
		SpringApplication.run(BadWeatherApplication.class, args);
	}

}
