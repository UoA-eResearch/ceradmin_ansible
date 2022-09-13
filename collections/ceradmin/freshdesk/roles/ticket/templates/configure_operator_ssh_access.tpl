<html>
    <head>
    </head>
    <body>
      Hi,
      <br><br>
      As part of a Nectar security upgrade in Auckland we will be installing a vulnerability scanner on Linux VMs.
      <br><br>
      In your project <i>{{ item.project_name }}</i> you have the following Linux VM(s) with a public IP address:
      <br><br>

      <table  border="3" width=auto style="border-collapse: collapse;">
      <tr>
          <th>VM name</th>
          <th>Nectar ID</th>
          <th>Operating System</th>
      </tr>
      {% for server in item.servers %}
      <tr>
        <td>{{ server['name'] }}</td>
        <td>{{ server['id'] }}</td>
        <td>{{ server['metadata']['os_family'] }} {{ server['metadata']['os_version'] }}</td>
      </tr>
      {% endfor %}
    </table>
    <br>
    To enable the installation of the vulnerability scanner we need you to configure
    a public SSH key on the VM(s), as described on the following page:
    <br><br>
    https://support.ehelp.edu.au/support/solutions/articles/6000256293-university-of-auckland-specific-configure-operator-public-ssh-key
    <br><br>
    Please do this before {{ item.done_by_date }} and let us know when you are done.<br>
    Don't hesitate to get in touch if you need a hand or you want to clarify something.<br>
    If you need more time, please reply to this e-mail and let us know by when you can look into this.
    <br><br>
    In case we don't hear back from you by {{ item.done_by_date }} we will unfortunately have
    to pause and lock the VM(s).<br>
    Once a VM is paused and locked you will not be able to log in and any services running
    on the VM will not respond. Essentially, the VM will appear frozen.<br>
    If this happens, do get in touch when you are ready to set up access for the Nectar@Auckland
    team, and we will resume normal operations of the VM.
    <br><br><br>

    Many thanks for paying attention to this matter,<br>
    Nectar@Auckland team, at the Centre for eResearch
  </body>
</html>
