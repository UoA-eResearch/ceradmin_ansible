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
    Please do this before {{ item.done_by_date }}, and don't hesitate to get in touch if you are not certain what we're asking for.<br>
    If you need more time, please reply to this e-mail and let us know by when you can look into this.<br>
    In case we don't hear back from you we will unfortunately have to disable access to the VM(s).
    <br><br><br>

    Many thanks,<br>
    Nectar@Auckland team, at the Centre for eResearch
  </body>
</html>
