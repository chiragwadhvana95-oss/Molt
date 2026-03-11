package com.example.forwarder;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Show message that app is running
        TextView textView = new TextView(this);
        textView.setText("SMS Forwarder is running...");
        setContentView(textView);
    }
}