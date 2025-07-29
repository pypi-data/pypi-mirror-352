package com.example.myapplication

import android.content.Context
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val username=findViewById<EditText>(R.id.ed1)
        val password=findViewById<EditText>(R.id.ed2)
        val save=findViewById<Button>(R.id.b1)
        val load=findViewById<Button>(R.id.b2)
        val clear=findViewById<Button>(R.id.b3)
        val delete=findViewById<Button>(R.id.b4)

        val shared_name=getSharedPreferences("addName", Context.MODE_PRIVATE)
        var edit=shared_name.edit()

        save.setOnClickListener{
            edit.putString("name",username.text.toString())
            edit.putString("password",password.text.toString())
            edit.commit()
            Toast.makeText(this, "Data Saved",Toast.LENGTH_LONG).show()

        }

        load.setOnClickListener {

            val getname = shared_name.getString("name", "default value")

            val getpass = shared_name.getString("password","default value")

            Toast.makeText(this,getname+" "+getpass,Toast.LENGTH_LONG).show()

        }

        clear.setOnClickListener {

            edit.remove("password")
            password.text.clear()

            edit.commit()

        }

        delete.setOnClickListener {

            edit.clear()
            username.text.clear()
            password.text.clear()

            edit.commit()

        }


    }
}