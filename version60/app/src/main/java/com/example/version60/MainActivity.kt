package com.example.version60

import android.os.Bundle
import android.view.MenuItem
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.fragment.app.Fragment
import com.example.projectvesion.Profile
import com.example.projectvesion.Search
import com.example.projectvesion.UploadData
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)


        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        val SearchFragment = Search()
        val uploadData = UploadData()
        val profile = Profile()

        makeCurrentFragmet(SearchFragment)

        val bottomNavigationView: BottomNavigationView = findViewById(R.id.bottomNavigation)
        bottomNavigationView.setOnItemSelectedListener { item: MenuItem ->
            when (item.itemId) {
                R.id.SearchBook -> {
                    makeCurrentFragmet(SearchFragment)
                    true
                }
                R.id.UploadData -> {
                    makeCurrentFragmet(uploadData)
                    true
                }
                R.id.home -> {
                    makeCurrentFragmet(profile)
                    true
                }
                else -> false
            }
        }
    }

    private fun makeCurrentFragmet(fragment: Fragment)= supportFragmentManager.beginTransaction().apply {
        replace(R.id.fl_wrapper,fragment)
        commit()

    }



}