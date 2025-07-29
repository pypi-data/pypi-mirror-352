package com.example.menufinal

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.option_menu_file, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.about -> {
                Toast.makeText(this, "About Selected", Toast.LENGTH_SHORT).show()
                return true
            }
            R.id.settings -> {
                Toast.makeText(this, "Settings Selected", Toast.LENGTH_SHORT).show()
                return true
            }
            R.id.exit -> {
                Toast.makeText(this, "Exit Selected", Toast.LENGTH_SHORT).show()
                return true
            }
        }
        return super.onOptionsItemSelected(item)
    }
}
