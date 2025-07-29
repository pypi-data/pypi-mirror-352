package com.example.myapplication



import android.content.DialogInterface
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.os.Message
import android.support.v7.app.AlertDialog
import android.widget.Button

class MainActivity : AppCompatActivity() {
    lateinit var showDialogMessage: Button
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        showDialogMessage = findViewById(R.id.button)
        showDialogMessage.setOnClickListener{
            showAlertDialog()
        }
    }
    fun showAlertDialog(){
        var alertDialog=AlertDialog.Builder(this@MainActivity)
        alertDialog.setTitle("change")
            .setMessage("do you want to change change the text of the button")
            .setIcon(R.drawable.ic_baseline_warning_24)
            .setCancelable(false)
            .setNegativeButton("no",DialogInterface.OnClickListener{
                    dialogInterface,which->
                dialogInterface.cancel()
            })
            .setPositiveButton("Yes",DialogInterface.OnClickListener{
                    dialogInterface, which ->
                showDialogMessage.text="alert dialog"
            })
            .setNeutralButton("Later") { dialogInterface, _ ->
                // Optional: you can show a toast or do nothing
                dialogInterface.dismiss()
            }
        alertDialog.create().show()
    }
}