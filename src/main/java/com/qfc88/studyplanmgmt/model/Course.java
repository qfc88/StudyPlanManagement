package com.qfc88.studyplanmgmt.model;


import lombok.Data;
import jakarta.persistence.*;
import java.util.List;

@Data
@Entity
@Table(name = "courses")

public class Course {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    
    private Long id;
    private String code;
    private String name;
    private Integer credits;
    private String classId;
    private Integer capacity;

    @OneToMany(cascade = CascadeType.ALL)
    private List<Lesson> lessons;



    



}
